"""Main bank account implementation."""
from __future__ import annotations
from datetime import datetime
import hashlib
import json
from typing import List, Dict, Optional, Any, Tuple, ClassVar

from .utils import logger, transaction_context, transaction_logger, generate_id
from .models import (
    Transaction, TransactionType, TransactionResult, AccountStatus, 
    BalanceException, BankingInterface
)
from .security import SecurityManager
from .loan import LoanManager
from .account_linking import AccountLinking
from .ai_services import AIServices


class BankAccount(BankingInterface):
    """Main bank account class."""
    
    # Class variable tracking all accounts
    _all_accounts: ClassVar[Dict[str, 'BankAccount']] = {}
    
    def __init__(self, initialAmount: float, acctName: str, creditLimit: float = 200):
        """Initialize a new bank account."""
        if initialAmount < 0:
            raise ValueError("❌ Error: Initial balance cannot be negative.")
            
        self.balance = initialAmount
        self.savings = 0
        self.name = acctName
        self.transactions: List[Transaction] = []
        self.autoSavingsPercentage = 5  # Default auto-savings
        self.creditLimit = creditLimit
        self.credit_score = 500
        self.account_id = self._generate_account_id(acctName, initialAmount)
        self.provider = "Default"  # Bank provider (PalmPay, MoneyPoint, etc.)
        self.status = AccountStatus.ACTIVE
        self.last_transaction_time = datetime.now()  
        
        # Initialize component objects - composition pattern
        self.loan_manager = LoanManager(self)
        self.account_linking = AccountLinking(self)
        self.security = SecurityManager(self)
        
        # Register this account in the class registry
        BankAccount._all_accounts[self.account_id] = self
        
        logger.info(f"Account created: {acctName} (ID: {self.account_id}) with ${initialAmount:.2f}")
        print(f"✅ Account '{self.name}' created with balance: ${self.balance:.2f}\n")
    
    def __str__(self) -> str:
        """Override the string representation of the account."""
        return f"Account: {self.name} (ID: {self.account_id}) | Balance: ${self.balance:.2f} | Savings: ${self.savings:.2f}"
    
    def __repr__(self) -> str:
        """Override the developer representation."""
        return f"BankAccount(name='{self.name}', balance={self.balance:.2f}, savings={self.savings:.2f})"
    
    def __eq__(self, other) -> bool:
        """Override equality check for account comparison."""
        if not isinstance(other, BankAccount):
            return False
        return self.account_id == other.account_id
    
    def __hash__(self) -> int:
        """Make BankAccount hashable so it can be used in sets and dict keys."""
        return hash(self.account_id)

    def __add__(self, other):
        """Override addition operator to combine balances."""
        if isinstance(other, (int, float)):
            # Adding money to the account
            result = BankAccount(self.balance + other, self.name, self.creditLimit)
            result.savings = self.savings
            result.transactions = self.transactions.copy()
            return result
        elif isinstance(other, BankAccount):
            # Combining two accounts
            result = BankAccount(self.balance + other.balance, f"{self.name}+{other.name}", max(self.creditLimit, other.creditLimit)) 
            result.savings = self.savings + other.savings
            result.transactions = self.transactions.copy() + other.transactions.copy()
            return result
        else:
            raise TypeError(f"Cannot add BankAccount and {type(other)}.")
        
    def __sub__(self, other):
        """Override subtraction to withdraw money from account."""
        if isinstance(other, (int, float)):
            if self.balance - other < -self.creditLimit:
                raise BalanceException("❌ Insufficient funds for this operation.")
            result = BankAccount(self.balance - other, self.name, self.creditLimit)
            result.savings = self.savings
            result.transactions = self.transactions.copy()
            
            # Create transaction
            tx = Transaction(TransactionType.WITHDRAWAL, other, "Subtracted amount")
            result.add_transaction(tx)
            
            return result
        else:
            raise TypeError(f"Cannot subtract {type(other)} from BankAccount.")
    
    def __lt__(self, other) -> bool:
        """Compare if this account has less balance than another."""
        if isinstance(other, BankAccount):
            return self.balance < other.balance
        elif isinstance(other, (int, float)):
            return self.balance < other
        raise TypeError(f"Cannot compare BankAccount with {type(other)}")
    
    def __gt__(self, other) -> bool:
        """Compare if this account has more balance than another."""
        if isinstance(other, BankAccount):
            return self.balance > other.balance
        elif isinstance(other, (int, float)):
            return self.balance > other
        raise TypeError(f"Cannot compare BankAccount with {type(other)}")
    
    def __enter__(self):
        """Support for using accounts as context managers."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Handle context manager exit."""
        # Log any exceptions that occurred
        if exc_type is not None:
            logger.error(f"Exception during account context: {exc_type.__name__}: {exc_val}")
            return False  # Don't suppress the exception
        return True
    
    @classmethod
    def get_account_by_id(cls, account_id: str) -> Optional['BankAccount']:
        """
        Retrieve an account by its ID.
        
        This demonstrates a class method that accesses class state (the accounts registry).
        
        Args:
            account_id: Account ID to look up
            
        Returns:
            The account if found, None otherwise
        """
        return cls._all_accounts.get(account_id)
    
    @classmethod
    def get_all_accounts(cls) -> Dict[str, 'BankAccount']:
        """Get all registered accounts."""
        return cls._all_accounts.copy()
    
    @staticmethod
    def _generate_account_id(name: str, amount: float) -> str:
        """Generate a unique account ID using hashing."""
        seed = f"{name}{amount}{datetime.now()}"
        return hashlib.sha256(seed.encode()).hexdigest()[:12]
    
    def add_transaction(self, transaction: Transaction) -> None:
        """Add a transaction to the account history."""
        self.transactions.append(transaction)
        self.last_transaction_time = datetime.now()  # Update transaction time
    
    @transaction_logger
    def deposit(self, amount: float, description: str = "Deposited amount") -> TransactionResult:
        """Deposit money into the account with auto-savings."""
        # Check security first
        self.security.check_operation_allowed("deposit")
            
        with transaction_context(self):
            savingsAmount = amount * (self.autoSavingsPercentage / 100)
            self.balance += (amount - savingsAmount)
            self.savings += savingsAmount
            
            # Create and add transaction
            tx = Transaction(
                TransactionType.DEPOSIT, 
                amount, 
                f"{description} | Auto-Saved ${savingsAmount:.2f}", 
                self.provider
            )
            self.add_transaction(tx)
        
        print(f"✅ Deposited ${amount:.2f}. Auto-Saved: ${savingsAmount:.2f}\n")
        
        return TransactionResult(
            success=True,
            message=f"Deposited ${amount:.2f}. Auto-Saved: ${savingsAmount:.2f}",
            amount=amount,
            new_balance=self.balance
        )

    @transaction_logger
    def withdraw(self, amount: float, description: str = "Withdrew amount") -> TransactionResult:
        """Withdraw money from the account."""
        if self.security.locked:
            return TransactionResult(
                success=False,
                message=f"Withdrawal Failed: Account '{self.name}' is LOCKED",
                amount=amount, 
                new_balance=self.balance
            )
            
        if self.balance - amount >= -self.creditLimit:
            with transaction_context(self):
                self.balance -= amount
                
                # Create and add transaction
                tx = Transaction(
                    TransactionType.WITHDRAWAL,
                    amount, 
                    description, 
                    self.provider
                )
                self.add_transaction(tx)
            
            print(f"✅ Withdrawn ${amount:.2f}. New balance: ${self.balance:.2f}\n")
            
            return TransactionResult(
                success=True,
                message=f"Withdrawn ${amount:.2f}. New balance: ${self.balance:.2f}",
                amount=amount,
                new_balance=self.balance
            )
        else:
            print("❌ Insufficient funds, even with overdraft.\n")
            
            return TransactionResult(
                success=False,
                message="Insufficient funds, even with overdraft",
                amount=amount,
                new_balance=self.balance
            )
    
    # Delegation methods - demonstrate the composition pattern
    def borrow(self, amount: float, loan_type: str = 'personal') -> TransactionResult:
        """Borrow money using the loan manager."""
        return self.loan_manager.request_loan(amount, loan_type)
    
    def repay_loan(self, amount: float) -> TransactionResult:
        """Repay loan using the loan manager."""
        return self.loan_manager.repay_loan(amount)
    
    @transaction_logger
    def deduct_maintenance_fee(self) -> TransactionResult:
        """Deduct monthly maintenance fee."""
        fee = 5
        if self.balance - fee < -self.creditLimit:
            print(f"⚠ Insufficient funds to deduct maintenance fee.\n")
            
            return TransactionResult(
                success=False,
                message="Insufficient funds to deduct maintenance fee",
                amount=fee,
                new_balance=self.balance
            )
        else:
            with transaction_context(self):
                self.balance -= fee
                
                # Create and add transaction
                tx = Transaction(
                    TransactionType.FEE,
                    fee,
                    "Maintenance Fee Deducted",
                    self.provider
                )
                self.add_transaction(tx)
            
            print(f"⚠ Maintenance Fee Deducted: ${fee:.2f}. New Balance: ${self.balance:.2f}\n")
            
            return TransactionResult(
                success=True,
                message=f"Maintenance Fee Deducted: ${fee:.2f}",
                amount=fee,
                new_balance=self.balance
            )

    def lock_account(self) -> None:
        """Lock the account to prevent transactions."""
        self.security.lock_account()

    def unlock_account(self, verification_code: Optional[str] = None) -> bool:
        """Unlock the account to allow transactions."""
        return self.security.unlock_account(verification_code)

    def enable_auto_savings(self, percentage: float) -> None:
        """Set the auto-savings percentage for deposits."""
        if not (0 <= percentage <= 100):
            raise ValueError("❌ Error: Auto-savings percentage must be between 0 and 100.")
        self.autoSavingsPercentage = percentage
        logger.info(f"Auto-savings set to {percentage}% for {self.name}")
        print(f"💰 Auto-Savings enabled: {percentage}% of deposits will be saved.\n")

    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Convert currency using AI-predicted rates."""
        rate = AIServices.predict_currency_conversion(from_currency, to_currency)
        converted_amount = amount * rate
        print(f"💱 {amount:.2f} {from_currency} = {converted_amount:.2f} {to_currency} (Rate: {rate:.2f})\n")
        return converted_amount
    
    def serialize(self) -> Dict[str, Any]:
        """
        Serialize the account to a dictionary for storage or transmission.
        
        Returns:
            Dictionary representation of the account
        """
        return {
            'account_id': self.account_id,
            'name': self.name,
            'balance': self.balance,
            'savings': self.savings,
            'provider': self.provider,
            'credit_score': self.credit_score,
            'credit_limit': self.creditLimit,
            'auto_savings_percentage': self.autoSavingsPercentage,
            'status': self.status.value,
            'transactions': [t.to_dict() for t in self.transactions],
            'loan_balance': self.loan_manager.loan_balance,
            'interest_rate': self.loan_manager.interest_rate,
            'loan_history': self.loan_manager.loan_history,
            'linked_accounts': list(self.account_linking.external_ids.keys()),
            'last_transaction_time': str(self.last_transaction_time)  # Add this field
        }
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'BankAccount':
        """
        Create an account from serialized data.
        
        Args:
            data: Dictionary with account data
            
        Returns:
            Reconstructed BankAccount object
        """
        account = cls(data['balance'], data['name'], data['credit_limit'])
        
        # Restore basic properties
        account.account_id = data['account_id']
        account.savings = data['savings']
        account.provider = data['provider']
        account.credit_score = data['credit_score']
        account.autoSavingsPercentage = data['auto_savings_percentage']
        account.status = AccountStatus(data['status'])
        
        # Restore transactions
        account.transactions = [Transaction.from_dict(t) for t in data['transactions']]
        
        # Restore loan data
        account.loan_manager.loan_balance = data['loan_balance']
        account.loan_manager.interest_rate = data['interest_rate']
        account.loan_manager.loan_history = data['loan_history']
        
        # Restore last transaction time if available
        if 'last_transaction_time' in data:
            try:
                account.last_transaction_time = datetime.fromisoformat(data['last_transaction_time'])
            except (ValueError, TypeError):
                # If there's any issue parsing the datetime, use current time
                account.last_transaction_time = datetime.now()
        else:
            account.last_transaction_time = datetime.now()
        
        return account
    
    # Delegation methods for account linking
    def link_external_account(self, external_account) -> bool:
        """Link an external bank account to this primary account."""
        return self.account_linking.link_account(external_account)

    def unlink_account(self, provider_name: str) -> bool:
        """Unlink an external account by provider name."""
        return self.account_linking.unlink_account(provider_name)

    def get_consolidated_balance(self) -> Tuple[float, float]:
        """Get total balance across all linked accounts."""
        return self.account_linking.get_consolidated_balance()
        
    def transfer_between_accounts(self, to_provider: str, amount: float) -> TransactionResult:
        """Transfer money between linked accounts."""
        return self.account_linking.transfer_between_accounts(to_provider, amount)

    def full_transaction_history(self) -> List[Transaction]:
        """Get transaction history from all linked accounts."""
        all_transactions = self.transactions.copy()
        
        print(f"📜 Full Transaction History Across All Accounts:")
        print(f"🔹 Primary Account ({self.name}):")
        
        if not self.transactions:
            print("   ℹ No transactions yet.\n")
        else:
            for transaction in self.transactions:
                print(f"   ↪ {transaction}")
                
        for account in self.account_linking.linked_accounts:
            print(f"🔹 {account.provider} Account ({account.name}):")
            if not account.transactions:
                print("   ℹ No transactions yet.\n") 
            else:
                for transaction in account.transactions:
                    print(f"   ↪ {transaction}")
                    all_transactions.append(transaction)
                    
        return all_transactions

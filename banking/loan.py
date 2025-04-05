"""Loan management functionality for the banking system."""
from datetime import datetime
from typing import Dict, List, Any, Final, Literal

from .utils import logger, transaction_context, transaction_logger
from .models import Transaction, TransactionType, TransactionResult


class LoanManager:
    """Class to handle loan-related operations."""
    
    # Default interest rates as a constant
    DEFAULT_RATES: Final[Dict[str, float]] = {
        'personal': 0.05,    # 5%
        'auto': 0.035,       # 3.5%
        'mortgage': 0.025,   # 2.5%
        'business': 0.06     # 6%
    }
    
    def __init__(self, account):
        """Initialize the loan manager."""
        self.account = account
        self.loan_balance = 0
        self.interest_rate = self.DEFAULT_RATES['personal']
        self.payment_schedule = []
        self.loan_history: List[Dict[str, Any]] = []
        
    @transaction_logger
    def request_loan(
        self, 
        amount: float, 
        loan_type: Literal['personal', 'auto', 'mortgage', 'business'] = 'personal'
    ) -> TransactionResult:
        """
        Request a loan for the specified amount.
        
        Args:
            amount: Requested loan amount
            loan_type: Type of loan requested
            
        Returns:
            TransactionResult with details of the operation
        """
        if self.loan_balance > 0:
            return TransactionResult(
                success=False,
                message="Loan Request Denied: You have an active loan",
                amount=amount,
                new_balance=self.account.balance
            )
            
        max_borrowable = self.predict_loan_approval(amount, loan_type)
        if amount > max_borrowable:
            return TransactionResult(
                success=False,
                message=f"Loan Request Denied: Max you can borrow is ${max_borrowable:.2f}",
                amount=amount,
                new_balance=self.account.balance
            )
        
        # Set appropriate interest rate
        self.interest_rate = self.DEFAULT_RATES.get(loan_type, self.DEFAULT_RATES['personal'])
            
        # Process loan in a thread-safe manner
        with transaction_context(self.account):
            self.loan_balance = amount
            self.account.balance += amount
            self.account.credit_score -= 30
            
            # Create transaction record
            transaction = Transaction(
                TransactionType.LOAN, 
                amount, 
                f"Loan approved: {loan_type} loan", 
                self.account.provider
            )
            self.account.add_transaction(transaction)
            
            # Record in loan history
            self.loan_history.append({
                'date': datetime.now().isoformat(),
                'amount': amount,
                'interest_rate': self.interest_rate,
                'loan_type': loan_type,
                'status': 'active'
            })
        
        logger.info(f"Loan approved for {self.account.name}: ${amount:.2f} ({loan_type} loan at {self.interest_rate*100:.1f}%)")
        print(f"✅ Loan Approved! Borrowed ${amount:.2f}. New Balance: ${self.account.balance:.2f}\n")
        
        return TransactionResult(
            success=True,
            message=f"Loan Approved! Borrowed ${amount:.2f}",
            amount=amount,
            new_balance=self.account.balance
        )
        
    @transaction_logger
    def repay_loan(self, amount: float) -> TransactionResult:
        """
        Repay a portion or all of an existing loan.
        
        Args:
            amount: Amount to repay
            
        Returns:
            TransactionResult with details of the operation
        """
        if amount > self.loan_balance:
            return TransactionResult(
                success=False,
                message="You can't repay more than your loan balance",
                amount=amount,
                new_balance=self.account.balance
            )
            
        if self.account.balance < amount:
            return TransactionResult(
                success=False,
                message="Insufficient funds to repay loan",
                amount=amount,
                new_balance=self.account.balance
            )
            
        with transaction_context(self.account):
            self.account.balance -= amount
            self.loan_balance -= amount
            self.account.credit_score += 20
            
            transaction = Transaction(
                TransactionType.REPAYMENT, 
                amount, 
                "Repaid loan amount", 
                self.account.provider
            )
            self.account.add_transaction(transaction)
            
            # Update loan history
            if self.loan_balance == 0:
                self.loan_history[-1]['status'] = 'repaid'
        
        logger.info(f"Loan payment of ${amount:.2f} processed for {self.account.name}")
        print(f"✅ Repaid ${amount:.2f}. Remaining Loan: ${self.loan_balance:.2f}\n")
        
        return TransactionResult(
            success=True,
            message=f"Repaid ${amount:.2f}. Remaining Loan: ${self.loan_balance:.2f}",
            amount=amount,
            new_balance=self.account.balance
        )
        
    def predict_loan_approval(self, requested_amount: float, loan_type: str = 'personal') -> float:
        """
        AI-based loan approval prediction.
        
        Args:
            requested_amount: Loan amount requested by the user
            loan_type: Type of loan being requested
            
        Returns:
            Maximum amount that would be approved
        """
        # Different loan types have different approval algorithms
        if loan_type == 'personal':
            max_loan = self.account.credit_score * 2
        elif loan_type == 'auto':
            max_loan = self.account.credit_score * 3
        elif loan_type == 'mortgage':
            max_loan = self.account.credit_score * 10
        elif loan_type == 'business':
            max_loan = self.account.credit_score * 5
        else:
            max_loan = self.account.credit_score * 1.5
            
        return min(max_loan, requested_amount)

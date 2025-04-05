"""Account linking functionality for multi-bank integration."""
import threading
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor

from .utils import logger, transaction_context, transaction_logger
from .models import Transaction, TransactionType, TransactionResult


class AccountLinking:
    """Class to handle multi-bank account linking."""
    
    def __init__(self, primary_account):
        """Initialize the account linking manager."""
        self.primary_account = primary_account
        self.linked_accounts = []
        self.external_ids = {}
        self._lock = threading.RLock()  # Re-entrant lock for thread safety
        
    def link_account(self, external_account) -> bool:
        """Link an external bank account to the primary account."""
        # Thread safety with a lock
        with self._lock:
            if external_account.account_id == self.primary_account.account_id:
                logger.warning(f"Attempted to link account to itself: {self.primary_account.name}")
                print(f"❌ Cannot link an account to itself.\n")
                return False
                
            # Check if account is already linked
            for account in self.linked_accounts:
                if account.account_id == external_account.account_id:
                    print(f"ℹ️ Account '{external_account.name}' is already linked.\n")
                    return False
                    
            self.linked_accounts.append(external_account)
            self.external_ids[external_account.provider] = external_account.account_id
            
            logger.info(f"Account linked: {external_account.name} from {external_account.provider}")
            print(f"✅ Successfully linked '{external_account.name}' from {external_account.provider}.\n")
            return True
        
    def unlink_account(self, provider_name: str) -> bool:
        """Unlink an external account by provider name."""
        with self._lock:
            if provider_name not in self.external_ids:
                print(f"❌ No linked account from {provider_name}.\n")
                return False
                
            account_id = self.external_ids[provider_name]
            for i, account in enumerate(self.linked_accounts):
                if account.account_id == account_id:
                    removed = self.linked_accounts.pop(i)
                    del self.external_ids[provider_name]
                    
                    logger.info(f"Account unlinked: {removed.name} from {provider_name}")
                    print(f"✅ Unlinked account '{removed.name}' from {provider_name}.\n")
                    return True
                    
            return False
        
    def get_consolidated_balance(self) -> Tuple[float, float]:
        """Get total balance across all linked accounts."""
        with self._lock:
            total_balance = self.primary_account.balance
            total_savings = self.primary_account.savings
            
            # Using ThreadPoolExecutor for parallel processing
            def get_account_balances(account):
                # In a real system, this might involve API calls to external banks
                return account.balance, account.savings
            
            # Process accounts in parallel for better performance with many accounts
            with ThreadPoolExecutor(max_workers=10) as executor:
                results = list(executor.map(get_account_balances, self.linked_accounts))
                
            for bal, sav in results:
                total_balance += bal
                total_savings += sav
                
            print(f"💰 Consolidated Balance: ${total_balance:.2f} | Total Savings: ${total_savings:.2f}\n")
            return total_balance, total_savings
        
    @transaction_logger
    def transfer_between_accounts(self, to_provider: str, amount: float) -> TransactionResult:
        """Transfer money between linked accounts."""
        with self._lock:
            if to_provider not in self.external_ids:
                return TransactionResult(
                    success=False,
                    message=f"No linked account from {to_provider}",
                    amount=amount,
                    new_balance=self.primary_account.balance
                )
                
            if self.primary_account.balance < amount:
                return TransactionResult(
                    success=False,
                    message=f"Insufficient funds to transfer ${amount:.2f}",
                    amount=amount,
                    new_balance=self.primary_account.balance
                )
                
            # Find the target account
            target_account = None
            for account in self.linked_accounts:
                if account.provider == to_provider:
                    target_account = account
                    break
                    
            if not target_account:
                return TransactionResult(
                    success=False,
                    message=f"Could not find account from {to_provider}",
                    amount=amount,
                    new_balance=self.primary_account.balance
                )
            
            # Execute transfer with transaction safety
            with transaction_context(self.primary_account), transaction_context(target_account):
                self.primary_account.balance -= amount
                target_account.balance += amount
                
                # Create transactions
                source_tx = Transaction(
                    TransactionType.TRANSFER, 
                    amount, 
                    f"Transferred to {to_provider} account", 
                    self.primary_account.provider
                )
                target_tx = Transaction(
                    TransactionType.TRANSFER, 
                    amount, 
                    f"Received from {self.primary_account.provider} account", 
                    to_provider
                )
                
                self.primary_account.add_transaction(source_tx)
                target_account.add_transaction(target_tx)
            
            logger.info(f"Transfer completed: ${amount:.2f} from {self.primary_account.name} to {target_account.name}")
            print(f"✅ Transferred ${amount:.2f} to {to_provider} account ({target_account.name}).\n")
            
            return TransactionResult(
                success=True,
                message=f"Transferred ${amount:.2f} to {to_provider} account",
                amount=amount,
                new_balance=self.primary_account.balance
            )

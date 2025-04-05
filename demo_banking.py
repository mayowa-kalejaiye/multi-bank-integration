"""
Banking System Demo Application

This script demonstrates the modular banking system with multiple components
and multi-bank integration.
"""
import sys
import os
import json

# Add the parent directory to sys.path to allow importing the banking package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from banking import BankAccount, SecurityException

def main():
    """Run the banking system demonstration."""
    print("\n🌐 DEMONSTRATION OF MODULAR BANKING SYSTEM")
    print("=" * 60)

    # Create accounts with different providers
    print("\n📱 CREATING ACCOUNTS WITH DIFFERENT PROVIDERS")
    primary = BankAccount(2000, "Primary Account")
    primary.provider = "WarpSpeed"
    print(f"Account created: {primary}")

    palmpay = BankAccount(500, "PalmPay Account") 
    palmpay.provider = "PalmPay"
    print(f"Account created: {palmpay}")

    moneypoint = BankAccount(750, "MoneyPoint Account")
    moneypoint.provider = "MoneyPoint"
    print(f"Account created: {moneypoint}")

    # Link external accounts to primary
    print("\n🔗 LINKING ACCOUNTS")
    primary.link_external_account(palmpay)
    primary.link_external_account(moneypoint)

    # Check consolidated balance
    print("\n💰 CHECKING CONSOLIDATED BALANCE")
    primary.get_consolidated_balance()

    # Make transactions on different accounts
    print("\n💸 MAKING TRANSACTIONS")
    palmpay.deposit(200, "Salary deposit")
    moneypoint.withdraw(50, "ATM withdrawal")

    # Transfer between accounts
    print("\n🔄 TRANSFERRING BETWEEN ACCOUNTS")
    primary.transfer_between_accounts("PalmPay", 300)

    # Use loan manager
    print("\n💵 LOAN MANAGEMENT")
    primary.borrow(500, "personal")
    primary.repay_loan(200)

    # View consolidated transaction history
    print("\n📊 TRANSACTION HISTORY")
    primary.full_transaction_history()
    
    # Demonstrate security features
    print("\n🔒 SECURITY FEATURE DEMONSTRATION")
    primary.lock_account()
    
    try:
        # This should fail because the account is locked
        primary.withdraw(100)
    except SecurityException as e:
        print(f"As expected, withdraw failed: {e}")
    
    primary.unlock_account("1234")
    primary.withdraw(100, "Now works after unlocking")
    
    # Demonstrate serialization
    print("\n💾 ACCOUNT SERIALIZATION DEMONSTRATION")
    account_data = primary.serialize()
    print(f"Account serialized to JSON with {len(account_data)} fields")
    
    # Save to a file (demonstration)
    with open("primary_account.json", "w") as f:
        json.dump(account_data, f, indent=2)
    print(f"Account data saved to 'primary_account.json'")
    
    # Demonstrate currency conversion
    print("\n💱 CURRENCY CONVERSION")
    amount_usd = 100
    primary.convert_currency(amount_usd, "USD", "EUR")
    primary.convert_currency(amount_usd, "USD", "GBP")

if __name__ == "__main__":
    main()

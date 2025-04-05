"""
Banking System Demo Application

This script demonstrates the modular banking system with multiple components
and multi-bank integration, including robust handling of edge cases.
"""
from datetime import datetime
import sys
import os
import json
import time
import random
import traceback

# Add the parent directory to sys.path to allow importing the banking package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from banking import BankAccount, SecurityException
from banking.models import TransactionType, BalanceException

def run_with_error_handling(func, error_msg, *args, **kwargs):
    """Run a function with comprehensive error handling."""
    try:
        return func(*args, **kwargs), None
    except Exception as e:
        print(f"❌ {error_msg}: {str(e)}")
        return None, e

def main():
    """Run the banking system demonstration with comprehensive edge case handling."""
    print("\n🌐 WARPSPEED BANKING SYSTEM DEMONSTRATION")
    print("=" * 60)
    print("This demo exercises all components of the banking system and tests edge cases")
    print("=" * 60)
    
    # Dictionary to store all operation results
    operation_results = {
        "account_creation": [],
        "transactions": [],
        "transfers": [],
        "loans": [],
        "balances": [],
        "currency_conversions": [],
        "security_tests": [],
        "operator_tests": [],
        "auto_savings_tests": [],
        "edge_cases": []
    }

    # SECTION 1: BASIC ACCOUNT OPERATIONS
    print("\n📋 SECTION 1: BASIC ACCOUNT OPERATIONS")
    print("-" * 40)
    
    # 1.1: Create accounts with different providers
    print("\n📱 Creating accounts with different providers")
    
    # Test edge case: Create account with negative balance
    print("\n🔍 EDGE CASE: Attempt to create account with negative balance")
    try:
        negative_account = BankAccount(-500, "Negative Balance Account")
        print("❌ ERROR: Account created with negative balance! This should not happen.")
        operation_results["edge_cases"].append({
            "case": "negative_balance_creation",
            "expected": "error",
            "actual": "success",
            "success": False
        })
    except ValueError as e:
        print(f"✅ Correctly prevented: {e}")
        operation_results["edge_cases"].append({
            "case": "negative_balance_creation",
            "expected": "error",
            "actual": "error",
            "success": True,
            "error": str(e)
        })
    
    # Create valid accounts
    print("\n✅ Creating valid accounts:")
    primary = BankAccount(2000, "Primary Account")
    primary.provider = "WarpSpeed"
    print(f"✓ Created: {primary}")
    
    palmpay = BankAccount(500, "PalmPay Account") 
    palmpay.provider = "PalmPay"
    print(f"✓ Created: {palmpay}")
    
    moneypoint = BankAccount(750, "MoneyPoint Account")
    moneypoint.provider = "MoneyPoint"
    print(f"✓ Created: {moneypoint}")
    
    zero_account = BankAccount(0, "Zero Balance Account")
    zero_account.provider = "ZeroBank"
    print(f"✓ Created: {zero_account}")
    
    # Record account creations
    operation_results["account_creation"] = [
        {"name": a.name, "provider": a.provider, "initial_balance": a.balance, "id": a.account_id}
        for a in [primary, palmpay, moneypoint, zero_account]
    ]
    
    # 1.2: Test deposit and withdrawal operations
    print("\n💰 Testing basic transactions")
    
    # Standard deposit
    print("\n▶ Standard deposit operation:")
    deposit_result, error = run_with_error_handling(
        primary.deposit, "Deposit failed", 500, "Regular deposit"
    )
    if deposit_result:
        print(f"✅ Deposited $500. New balance: ${primary.balance:.2f}, Savings: ${primary.savings:.2f}")
    
    # Standard withdrawal
    print("\n▶ Standard withdrawal operation:")
    withdraw_result, error = run_with_error_handling(
        primary.withdraw, "Withdrawal failed", 200, "Regular withdrawal"
    )
    if withdraw_result:
        print(f"✅ Withdrew $200. New balance: ${primary.balance:.2f}")
    
    # Edge case: Withdrawal exceeding balance but within credit limit
    print("\n🔍 EDGE CASE: Withdrawal exceeding balance but within credit limit")
    credit_withdrawal, error = run_with_error_handling(
        zero_account.withdraw, "Credit withdrawal failed", 150, "Using credit line"
    )
    if credit_withdrawal:
        print(f"✅ Credit withdrawal succeeded. Balance: ${zero_account.balance:.2f} (negative)")
        operation_results["edge_cases"].append({
            "case": "credit_withdrawal",
            "account": zero_account.name,
            "amount": 150,
            "new_balance": zero_account.balance,
            "success": True
        })
    else:
        print("❌ Credit withdrawal should have succeeded within credit limit")
        operation_results["edge_cases"].append({
            "case": "credit_withdrawal",
            "success": False,
            "error": str(error) if error else "Unknown error"
        })
    
    # Edge case: Withdrawal exceeding credit limit
    print("\n🔍 EDGE CASE: Withdrawal exceeding credit limit")
    try:
        exceed_credit = zero_account.withdraw(500, "Exceeding credit limit")
        print(f"❌ ERROR: Allowed withdrawal exceeding credit limit! Balance: ${zero_account.balance:.2f}")
        operation_results["edge_cases"].append({
            "case": "exceed_credit_limit",
            "expected": "error or false result",
            "actual": "success",
            "success": False
        })
    except BalanceException as e:
        print(f"✅ Correctly prevented: {e}")
        operation_results["edge_cases"].append({
            "case": "exceed_credit_limit",
            "expected": "error or false result",
            "actual": "error",
            "success": True,
            "error": str(e)
        })
    
    # Record transaction results
    operation_results["transactions"].extend([
        {
            "type": "deposit",
            "account": primary.name,
            "amount": 500,
            "description": "Regular deposit",
            "success": deposit_result is not None,
            "new_balance": primary.balance if deposit_result else None
        },
        {
            "type": "withdrawal",
            "account": primary.name,
            "amount": 200,
            "description": "Regular withdrawal", 
            "success": withdraw_result is not None,
            "new_balance": primary.balance if withdraw_result else None
        }
    ])
    
    # SECTION 2: MULTI-BANK INTEGRATION
    print("\n📋 SECTION 2: MULTI-BANK INTEGRATION")
    print("-" * 40)
    
    # 2.1: Link accounts
    print("\n🔗 Linking external accounts to primary account")
    
    # Link valid accounts
    palmpay_link_result = primary.link_external_account(palmpay)
    moneypoint_link_result = primary.link_external_account(moneypoint)
    
    if palmpay_link_result and moneypoint_link_result:
        print(f"✅ Successfully linked PalmPay and MoneyPoint accounts to primary")
        linked_count = len(primary.account_linking.linked_accounts)
        print(f"✅ Primary account now has {linked_count} linked accounts")
    else:
        print("❌ Failed to link one or more accounts")
    
    # Edge case: Link account to itself
    print("\n🔍 EDGE CASE: Attempt to link account to itself")
    self_link_result = primary.link_external_account(primary)
    if not self_link_result:
        print("✅ Correctly prevented linking account to itself")
        operation_results["edge_cases"].append({
            "case": "self_linking",
            "expected": False,
            "actual": self_link_result,
            "success": True
        })
    else:
        print("❌ ERROR: Allowed account to link to itself!")
        operation_results["edge_cases"].append({
            "case": "self_linking",
            "expected": False,
            "actual": self_link_result,
            "success": False
        })
    
    # Edge case: Link already linked account
    print("\n🔍 EDGE CASE: Attempt to link already linked account")
    duplicate_link = primary.link_external_account(palmpay)
    if not duplicate_link:
        print("✅ Correctly prevented linking already linked account")
        operation_results["edge_cases"].append({
            "case": "duplicate_linking",
            "expected": False,
            "actual": duplicate_link,
            "success": True
        })
    else:
        print("❌ ERROR: Allowed linking the same account twice!")
        operation_results["edge_cases"].append({
            "case": "duplicate_linking",
            "expected": False,
            "actual": duplicate_link,
            "success": False
        })
    
    # 2.2: Consolidated view
    print("\n📊 Testing consolidated view of all accounts")
    total_balance, total_savings = primary.get_consolidated_balance()
    print(f"✅ Consolidated balance: ${total_balance:.2f}, Consolidated savings: ${total_savings:.2f}")
    
    # Verify math matches individual accounts
    expected_balance = primary.balance + palmpay.balance + moneypoint.balance
    expected_savings = primary.savings + palmpay.savings + moneypoint.savings
    
    if abs(total_balance - expected_balance) < 0.01 and abs(total_savings - expected_savings) < 0.01:
        print("✅ Consolidated balances correctly calculated")
    else:
        print(f"❌ ERROR: Consolidated balance calculation error!")
        print(f"   Expected: ${expected_balance:.2f}, Got: ${total_balance:.2f}")
    
    operation_results["balances"].append({
        "timestamp": str(getattr(primary, 'last_transaction_time', datetime.now())),
        "consolidated_balance": total_balance,
        "consolidated_savings": total_savings,
        "expected_balance": expected_balance,
        "expected_savings": expected_savings,
        "accounts_included": [a.name for a in [primary, palmpay, moneypoint]],
        "calculation_accurate": (abs(total_balance - expected_balance) < 0.01)
    })
    
    # 2.3: Inter-account transfers
    print("\n🔄 Testing transfers between accounts")
    
    # Standard transfer
    print("\n▶ Standard transfer operation:")
    before_primary = primary.balance
    before_palmpay = palmpay.balance
    
    transfer_result, error = run_with_error_handling(
        primary.transfer_between_accounts, "Transfer failed", "PalmPay", 300
    )
    
    if transfer_result and transfer_result.success:
        print(f"✅ Transferred $300 from {primary.name} to {palmpay.name}")
        print(f"   {primary.name} balance: ${primary.balance:.2f} (was ${before_primary:.2f})")
        print(f"   {palmpay.name} balance: ${palmpay.balance:.2f} (was ${before_palmpay:.2f})")
    else:
        print(f"❌ Transfer failed: {error if error else 'Unknown error'}")
    
    # Edge case: Transfer to non-existent account
    print("\n🔍 EDGE CASE: Transfer to non-existent account")
    invalid_transfer, error = run_with_error_handling(
        primary.transfer_between_accounts, "Invalid transfer failed", "NonExistentBank", 100
    )
    
    if invalid_transfer and invalid_transfer.success:
        print("❌ ERROR: Allowed transfer to non-existent account!")
        operation_results["edge_cases"].append({
            "case": "transfer_nonexistent",
            "expected": "error or false result",
            "actual": "success",
            "success": False
        })
    else:
        print(f"✅ Correctly prevented transfer to non-existent account: {error if error else 'Unknown error'}")
        operation_results["edge_cases"].append({
            "case": "transfer_nonexistent",
            "expected": "error or false result",
            "actual": "error",
            "success": True,
            "error": str(error) if error else "Result indicated failure"
        })
    
    # Edge case: Transfer amount exceeding balance + credit
    print("\n🔍 EDGE CASE: Transfer amount exceeding balance + credit limit")
    excessive_transfer, error = run_with_error_handling(
        primary.transfer_between_accounts, "Excessive transfer failed", "PalmPay", 10000
    )
    
    if excessive_transfer and excessive_transfer.success:
        print("❌ ERROR: Allowed transfer exceeding balance + credit limit!")
        operation_results["edge_cases"].append({
            "case": "transfer_excessive",
            "expected": "error or false result",
            "actual": "success",
            "success": False
        })
    else:
        print(f"✅ Correctly prevented excessive transfer: {error if error else 'Result indicated failure'}")
        operation_results["edge_cases"].append({
            "case": "transfer_excessive",
            "expected": "error or false result",
            "actual": "error",
            "success": True,
            "error": str(error) if error else "Result indicated failure"
        })
    
    operation_results["transfers"].append({
        "from_account": primary.name,
        "to_provider": "PalmPay",
        "amount": 300,
        "before_from_balance": before_primary,
        "after_from_balance": primary.balance,
        "before_to_balance": before_palmpay,
        "after_to_balance": palmpay.balance,
        "success": transfer_result is not None and transfer_result.success
    })
    
    # SECTION 3: LOAN MANAGEMENT
    print("\n📋 SECTION 3: LOAN MANAGEMENT")
    print("-" * 40)
    
    # 3.1: Borrowing
    print("\n💵 Testing loan functionality")
    print("\n▶ Standard loan request:")
    loan_result, error = run_with_error_handling(
        primary.borrow, "Loan request failed", 500, "personal"
    )
    
    if loan_result and loan_result.success:
        print(f"✅ Loan approved! Amount: $500, New balance: ${loan_result.new_balance:.2f}")
        print(f"   Current loan balance: ${primary.loan_manager.loan_balance:.2f}")
    else:
        print(f"❌ Loan request failed: {error if error else 'Unknown error'}")
    
    # Edge case: Excessive loan amount
    print("\n🔍 EDGE CASE: Request for excessive loan amount")
    huge_loan, error = run_with_error_handling(
        primary.borrow, "Huge loan request failed", 50000, "personal"
    )
    
    if huge_loan and huge_loan.success:
        print("❌ ERROR: Approved unreasonably large loan!")
        operation_results["edge_cases"].append({
            "case": "excessive_loan",
            "expected": "error or false result",
            "actual": "success",
            "success": False
        })
    else:
        print(f"✅ Correctly rejected excessive loan request: {error if error else 'Result indicated rejection'}")
        operation_results["edge_cases"].append({
            "case": "excessive_loan",
            "expected": "error or false result",
            "actual": "error or rejection",
            "success": True,
            "error": str(error) if error else "Result indicated rejection"
        })
    
    # 3.2: Loan repayment
    print("\n▶ Standard loan repayment:")
    repay_result, error = run_with_error_handling(
        primary.repay_loan, "Loan repayment failed", 200
    )
    
    if repay_result and repay_result.success:
        print(f"✅ Loan payment processed. Amount: $200")
        print(f"   Remaining loan balance: ${primary.loan_manager.loan_balance:.2f}")
    else:
        print(f"❌ Loan repayment failed: {error if error else 'Unknown error'}")
    
    # Edge case: Repay more than loan balance
    print("\n🔍 EDGE CASE: Repay more than current loan balance")
    overpayment, error = run_with_error_handling(
        primary.repay_loan, "Loan overpayment failed", 1000
    )
    
    # Record loan operations
    operation_results["loans"].extend([
        {
            "type": "borrow",
            "account": primary.name,
            "amount": 500,
            "loan_type": "personal",
            "success": loan_result is not None and loan_result.success,
            "new_balance": loan_result.new_balance if loan_result else None
        },
        {
            "type": "repay",
            "account": primary.name,
            "amount": 200,
            "success": repay_result is not None and repay_result.success,
            "remaining_loan": primary.loan_manager.loan_balance
        }
    ])
    
    # SECTION 4: SECURITY FEATURES
    print("\n📋 SECTION 4: SECURITY FEATURES")
    print("-" * 40)
    
    # 4.1: Account locking
    print("\n🔒 Testing account security features")
    
    # Lock account
    print("\n▶ Locking account:")
    primary.lock_account()
    print(f"✅ Account locked: {primary.security.locked}")
    
    # Try operation on locked account
    print("\n🔍 EDGE CASE: Attempt withdrawal on locked account")
    try:
        locked_withdrawal = primary.withdraw(100, "Should fail - account locked")
        if locked_withdrawal.success:
            print("❌ ERROR: Allowed withdrawal on locked account!")
            operation_results["edge_cases"].append({
                "case": "locked_withdrawal",
                "expected": "error or false result",
                "actual": "success",
                "success": False
            })
        else:
            print(f"✅ Correctly prevented withdrawal on locked account")
            operation_results["edge_cases"].append({
                "case": "locked_withdrawal",
                "expected": "error or false result",
                "actual": "rejection",
                "success": True
            })
    except SecurityException as e:
        print(f"✅ Correctly threw exception: {e}")
        operation_results["edge_cases"].append({
            "case": "locked_withdrawal",
            "expected": "error or false result",
            "actual": "security exception",
            "success": True,
            "error": str(e)
        })
    
    # Unlock account
    print("\n▶ Unlocking account:")
    unlock_result = primary.unlock_account("1234")
    print(f"✅ Account unlocked successfully: {unlock_result}")
    print(f"   Account locked status: {primary.security.locked}")
    
    # Verify unlocked operations
    print("\n▶ Verifying operations after unlock:")
    post_unlock_withdrawal, error = run_with_error_handling(
        primary.withdraw, "Post-unlock withdrawal failed", 100, "After unlocking"
    )
    
    if post_unlock_withdrawal and post_unlock_withdrawal.success:
        print(f"✅ Post-unlock withdrawal successful: ${post_unlock_withdrawal.amount:.2f}")
    else:
        print(f"❌ Post-unlock withdrawal failed: {error if error else 'Unknown error'}")
    
    # SECTION 5: ADVANCED FEATURES
    print("\n📋 SECTION 5: ADVANCED FEATURES")
    print("-" * 40)
    
    # 5.1: Auto-savings configuration
    print("\n💰 Testing auto-savings functionality")
    
    # Check default
    print(f"✅ Default auto-savings percentage: {primary.autoSavingsPercentage}%")
    
    # Change percentage
    print("\n▶ Changing auto-savings percentage:")
    primary.enable_auto_savings(15)
    print(f"✅ New auto-savings percentage: {primary.autoSavingsPercentage}%")
    
    # Test with deposit
    print("\n▶ Testing deposit with new auto-savings rate:")
    deposit_amount = 1000
    savings_before = primary.savings
    
    auto_savings_deposit, error = run_with_error_handling(
        primary.deposit, "Auto-savings deposit failed", deposit_amount, "Testing auto-savings"
    )
    
    if auto_savings_deposit and auto_savings_deposit.success:
        expected_savings = deposit_amount * (primary.autoSavingsPercentage / 100)
        actual_savings_increase = primary.savings - savings_before
        
        print(f"✅ Deposit with auto-savings: ${deposit_amount:.2f}")
        print(f"   Expected amount to savings: ${expected_savings:.2f}")
        print(f"   Actual savings increase: ${actual_savings_increase:.2f}")
        
        if abs(expected_savings - actual_savings_increase) < 0.01:
            print("✅ Auto-savings calculation correct")
        else:
            print("❌ ERROR: Auto-savings calculation incorrect!")
    else:
        print(f"❌ Auto-savings deposit failed: {error if error else 'Unknown error'}")
    
    operation_results["auto_savings_tests"].append({
        "original_percentage": 5,
        "new_percentage": 15,
        "deposit_amount": deposit_amount,
        "savings_before": savings_before,
        "savings_after": primary.savings,
        "savings_increase": primary.savings - savings_before,
        "expected_increase": deposit_amount * 0.15,
        "calculation_accurate": abs((primary.savings - savings_before) - (deposit_amount * 0.15)) < 0.01
    })
    
    # 5.2: Transaction safety with context manager
    print("\n⚡ Testing transaction context safety")
    
    safety_account = BankAccount(100, "Safety Test Account")
    original_balance = safety_account.balance
    
    print(f"✅ Created test account with balance: ${original_balance:.2f}")
    print("\n🔍 EDGE CASE: Operation that fails mid-transaction")
    
    try:
        with safety_account as acct:
            # First part - would succeed
            acct.balance += 50
            print(f"   Interim balance change: ${acct.balance:.2f}")
            
            # Simulate failure
            raise ValueError("Simulated transaction failure")
            
            # Should not reach here
            acct.balance += 50
    except ValueError:
        print(f"✅ Transaction intentionally failed")
        print(f"   Original balance: ${original_balance:.2f}")
        print(f"   Current balance: ${safety_account.balance:.2f}")
        
        if safety_account.balance == original_balance:
            print("✅ Transaction safety correctly rolled back changes")
        else:
            print("❌ ERROR: Transaction context did not roll back changes!")
    
    operation_results["transactions"].append({
        "type": "transaction_safety_test",
        "account": safety_account.name,
        "original_balance": original_balance,
        "final_balance": safety_account.balance,
        "rollback_successful": safety_account.balance == original_balance
    })
    
    # 5.3: Currency conversion
    print("\n💱 Testing currency conversion")
    
    amount_usd = 100
    
    # Convert to EUR
    eur_result, error = run_with_error_handling(
        primary.convert_currency, "EUR conversion failed", amount_usd, "USD", "EUR"
    )
    
    if eur_result is not None:
        print(f"✅ Converted ${amount_usd:.2f} USD to {eur_result:.2f} EUR")
    else:
        print(f"❌ Currency conversion failed: {error if error else 'Unknown error'}")
    
    # Convert to GBP
    gbp_result, error = run_with_error_handling(
        primary.convert_currency, "GBP conversion failed", amount_usd, "USD", "GBP"
    )
    
    if gbp_result is not None:
        print(f"✅ Converted ${amount_usd:.2f} USD to {gbp_result:.2f} GBP")
    else:
        print(f"❌ Currency conversion failed: {error if error else 'Unknown error'}")
    
    operation_results["currency_conversions"].extend([
        {
            "from_currency": "USD",
            "to_currency": "EUR",
            "amount": amount_usd,
            "converted_amount": eur_result
        },
        {
            "from_currency": "USD",
            "to_currency": "GBP",
            "amount": amount_usd,
            "converted_amount": gbp_result
        }
    ])
    
    # 5.4: Operator overloading
    print("\n➕ Testing operator overloading")
    
    # Addition with number
    print("\n▶ Addition with number:")
    print(f"   Original account: {primary}")
    new_account = primary + 500
    print(f"✅ Result of account + 500: {new_account}")
    
    # Combination of accounts
    print("\n▶ Combining accounts:")
    print(f"   Account 1: {primary}")
    print(f"   Account 2: {palmpay}")
    combined_account = primary + palmpay
    print(f"✅ Combined account: {combined_account}")
    
    operation_results["operator_tests"].extend([
        {
            "operation": "addition",
            "original_balance": primary.balance,
            "amount_added": 500,
            "result_balance": new_account.balance
        },
        {
            "operation": "account_combination",
            "account1": primary.name,
            "account1_balance": primary.balance,
            "account2": palmpay.name,
            "account2_balance": palmpay.balance,
            "combined_balance": combined_account.balance,
            "calculation_accurate": abs(combined_account.balance - (primary.balance + palmpay.balance)) < 0.01
        }
    ])
    
    # SECTION 6: DATA SERIALIZATION
    print("\n📋 SECTION 6: DATA SERIALIZATION")
    print("-" * 40)
    
    # 6.1: Serialization
    print("\n💾 Testing account serialization")
    
    account_data = primary.serialize()
    print(f"✅ Account serialized to dictionary with {len(account_data)} fields")
    print(f"   Fields included: {', '.join(list(account_data.keys())[:5])}...")
    
    # Save to file with full path and error handling
    try:
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "primary_account.json")
        with open(file_path, "w") as f:
            json.dump(account_data, f, indent=2)
        print(f"✅ Account data saved to '{file_path}'")
    except Exception as e:
        print(f"❌ Error saving primary_account.json: {e}")
        traceback.print_exc()
    
    # 6.2: Deserialization
    print("\n📂 Testing account deserialization")
    
    try:
        # Load data back from file
        with open(os.path.join(os.path.dirname(__file__), "primary_account.json"), "r") as f:
            loaded_data = json.load(f)
        
        # Recreate account from data
        reconstructed = BankAccount.deserialize(loaded_data)
        print(f"✅ Account reconstructed from serialized data")
        print(f"   Original account: {primary}")
        print(f"   Reconstructed account: {reconstructed}")
        
        # Verify key attributes match
        checks_passed = True
        for attr in ['name', 'balance', 'savings', 'provider']:
            original = getattr(primary, attr)
            restored = getattr(reconstructed, attr)
            if original != restored:
                print(f"❌ ERROR: Attribute '{attr}' doesn't match. Original: {original}, Restored: {restored}")
                checks_passed = False
        
        if checks_passed:
            print("✅ All key attributes successfully restored")
        
    except Exception as e:
        print(f"❌ Deserialization failed: {e}")
        traceback.print_exc()
    
    # SECTION 7: SAVING RESULTS
    print("\n📋 SECTION 7: SAVING TEST RESULTS")
    print("-" * 40)
    
    # Save comprehensive operation results
    try:
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "operation_results.json")
        with open(file_path, "w") as f:
            json.dump(operation_results, f, indent=2)
        print(f"✅ Comprehensive operation results saved to '{file_path}'")
    except Exception as e:
        print(f"❌ Error saving operation_results.json: {e}")
        traceback.print_exc()
    
    # Create a complete store of all accounts
    try:
        account_store = {}
        for account_id, account in BankAccount.get_all_accounts().items():
            account_store[account_id] = account.serialize()
        
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "account_store.json")
        with open(file_path, "w") as f:
            json.dump(account_store, f, indent=2)
        print(f"✅ Complete account store saved to '{file_path}'")
    except Exception as e:
        print(f"❌ Error saving account_store.json: {e}")
        traceback.print_exc()
    
    # Summary 
    print("\n📊 DEMONSTRATION SUMMARY")
    print("=" * 60)
    print(f"✓ Created {len(BankAccount.get_all_accounts())} accounts")
    print(f"✓ Tested {len(operation_results['transactions'])} transactions")
    print(f"✓ Performed {len(operation_results['transfers'])} transfers")
    print(f"✓ Tested {len(operation_results['edge_cases'])} edge cases")
    print(f"✓ All banking system components exercised")
    print("=" * 60)

if __name__ == "__main__":
    main()

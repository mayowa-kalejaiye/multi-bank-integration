"""
Demonstration of method overriding in Python.

This example shows how a child class can override methods from its parent class,
which is a fundamental aspect of inheritance and polymorphism.
"""


class BankingProduct:
    """Base class for all banking products."""
    
    def __init__(self, name: str, balance: float = 0):
        """Initialize a banking product with name and balance."""
        self.name = name
        self.balance = balance
    
    def apply_interest(self) -> float:
        """
        Apply standard interest rate of 2% to the balance.
        
        This method will be overridden by child classes with
        their own interest calculation logic.
        
        Returns:
            The interest amount applied
        """
        interest_rate = 0.02  # 2% standard interest
        interest = self.balance * interest_rate
        self.balance += interest
        print(f"Applied {interest_rate*100}% interest (${interest:.2f}) to {self.name}")
        return interest
    
    def display_info(self) -> None:
        """Display basic information about the banking product."""
        print(f"Product: {self.name}, Balance: ${self.balance:.2f}")
    
    def deposit(self, amount: float) -> None:
        """Add funds to the balance."""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        print(f"Deposited ${amount:.2f} to {self.name}")


class SavingsAccount(BankingProduct):
    """
    Savings account that extends BankingProduct.
    
    This class demonstrates method overriding by providing
    a different implementation of the apply_interest method.
    """
    
    def __init__(self, name: str, balance: float = 0, interest_rate: float = 0.05):
        """
        Initialize a savings account with custom interest rate.
        
        Args:
            name: Account name
            balance: Initial balance
            interest_rate: Annual interest rate (default 5%)
        """
        # Call parent constructor first
        super().__init__(name, balance)
        self.interest_rate = interest_rate
    
    def apply_interest(self) -> float:
        """
        Override the parent's interest calculation with a higher rate.
        
        Returns:
            The interest amount applied
        """
        # This method overrides the parent method completely
        interest = self.balance * self.interest_rate
        self.balance += interest
        print(f"Applied {self.interest_rate*100}% savings interest (${interest:.2f}) to {self.name}")
        return interest
    
    def display_info(self) -> None:
        """
        Override display_info to show additional information.
        
        This method overrides the parent method but also calls it using super().
        """
        # Call the parent method first, then add our own functionality
        super().display_info()
        print(f"Type: Savings Account, Interest Rate: {self.interest_rate*100}%")


class CheckingAccount(BankingProduct):
    """
    Checking account that extends BankingProduct.
    
    This class partially overrides the parent methods.
    """
    
    def __init__(self, name: str, balance: float = 0, overdraft_limit: float = 100):
        """Initialize a checking account with overdraft limit."""
        super().__init__(name, balance)
        self.overdraft_limit = overdraft_limit
        self.transaction_count = 0
    
    def apply_interest(self) -> float:
        """
        Lower interest rate for checking accounts.
        
        Returns:
            The interest amount applied
        """
        # Checking accounts get lower interest
        interest_rate = 0.005  # 0.5%
        interest = self.balance * interest_rate
        self.balance += interest
        print(f"Applied {interest_rate*100}% checking interest (${interest:.2f}) to {self.name}")
        return interest
    
    def withdraw(self, amount: float) -> bool:
        """
        Withdraw funds with overdraft protection.
        
        Args:
            amount: Amount to withdraw
            
        Returns:
            True if withdrawal successful, False otherwise
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
            
        if self.balance - amount >= -self.overdraft_limit:
            self.balance -= amount
            self.transaction_count += 1
            print(f"Withdrew ${amount:.2f} from {self.name}")
            return True
        else:
            print(f"Insufficient funds in {self.name} (including overdraft protection)")
            return False
    
    def display_info(self) -> None:
        """Override to show checking-specific information."""
        super().display_info()
        print(f"Type: Checking Account, Overdraft Limit: ${self.overdraft_limit:.2f}")
        print(f"Transactions: {self.transaction_count}")


def demonstrate_override():
    """Show how method overriding works with different account types."""
    print("\n==== Method Overriding Demonstration ====\n")
    
    # Create base and derived class instances
    base_product = BankingProduct("Generic Account", 1000)
    savings = SavingsAccount("High-Yield Savings", 1000)
    checking = CheckingAccount("Everyday Checking", 1000, 200)
    
    # Demonstrate how the same method behaves differently for each class
    print("\n--- Applying Interest (Overridden Method) ---")
    base_product.apply_interest()     # Uses base implementation
    savings.apply_interest()          # Uses completely overridden implementation  
    checking.apply_interest()         # Uses another overridden implementation
    
    # Show information display
    print("\n--- Displaying Info (Overridden Method with super() call) ---")
    base_product.display_info()       # Base implementation
    savings.display_info()            # Overridden + parent implementation
    checking.display_info()           # Overridden + parent implementation
    
    # Demonstrate method that exists only in child class
    print("\n--- Withdraw Method (Only in CheckingAccount) ---")
    checking.withdraw(200)            # Method only in CheckingAccount
    
    # Show polymorphism with a list of different account types
    print("\n--- Polymorphism with List of Accounts ---")
    accounts = [base_product, savings, checking]
    for account in accounts:
        # The apply_interest method behaves differently based on the actual type
        account.apply_interest()      # Polymorphic behavior


if __name__ == "__main__":
    demonstrate_override()

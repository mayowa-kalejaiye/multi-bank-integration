"""Exceptions and data models for the banking system."""
from __future__ import annotations
from datetime import datetime, timedelta
import enum
import dataclasses
import hashlib
import random
from typing import List, Dict, Union, Optional, ClassVar, Any, Literal, Protocol

# Exception hierarchy
class BalanceException(Exception):
    """Custom exception for balance-related errors."""
    pass


class SecurityException(Exception):
    """Custom exception for security-related errors."""
    pass


class LinkingException(Exception):
    """Custom exception for account linking errors."""
    pass


# Enums for type safety
class TransactionType(enum.Enum):
    """
    Enumeration of transaction types.
    
    This demonstrates Python's enum module which provides symbolic names for a set
    of related values, making code more readable and type-safe.
    """
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer" 
    LOAN = "loan"
    REPAYMENT = "repayment"
    FEE = "fee"
    INTEREST = "interest"
    
    def __str__(self) -> str:
        return self.value


class AccountStatus(enum.Enum):
    """Enumeration of possible account statuses"""
    ACTIVE = "active"
    LOCKED = "locked"
    SUSPENDED = "suspended"
    CLOSED = "closed"


# Protocols for structural typing
class Lockable(Protocol):
    """
    Protocol defining objects that can be locked.
    
    This demonstrates Python's Protocol class which enables structural typing
    (similar to interfaces in other languages, but based on behavior rather than 
    explicit declarations).
    """
    @property
    def locked(self) -> bool: ...
    
    def lock_account(self) -> None: ...
    
    def unlock_account(self, verification_code: Optional[str] = None) -> bool: ...


# Dataclasses for simplified data containers
@dataclasses.dataclass
class TransactionResult:
    """
    Data class to represent the result of a transaction.
    
    This demonstrates Python's dataclass decorator which automatically generates
    special methods like __init__, __repr__, and __eq__ for classes that primarily
    store data, reducing boilerplate code.
    """
    success: bool
    message: str
    amount: float
    new_balance: float
    timestamp: datetime = dataclasses.field(default_factory=datetime.now)
    transaction_id: str = dataclasses.field(default_factory=lambda: hashlib.md5(str(random.random()).encode()).hexdigest())


@dataclasses.dataclass(frozen=True)
class BankingCredential:
    """
    Immutable data class for storing banking credentials.
    
    The frozen=True parameter makes this class immutable, providing safety
    for sensitive data like credentials.
    """
    provider: str
    api_key: str
    url: str
    username: Optional[str] = None
    
    # Post-initialization processing to hash any sensitive values
    def __post_init__(self):
        # dataclasses.replace is used since frozen=True prevents direct assignment
        object.__setattr__(self, 'api_key', hashlib.sha256(self.api_key.encode()).hexdigest())
        if self.username:
            object.__setattr__(self, 'username', hashlib.sha256(self.username.encode()).hexdigest())


class Transaction:
    """Class to represent individual transactions."""
    
    # Class variables shared by all instances
    transaction_count: ClassVar[int] = 0
    
    def __init__(
        self, 
        transaction_type: Union[TransactionType, str], 
        amount: float, 
        description: str = "", 
        provider: str = "Default"
    ):
        """Initialize a new transaction."""
        self.timestamp = datetime.now()
        self.transaction_id = f"{provider}-{self.timestamp.strftime('%Y%m%d%H%M%S')}-{Transaction.transaction_count}"
        
        # Convert string to enum if needed
        if isinstance(transaction_type, str):
            try:
                self.transaction_type = TransactionType(transaction_type)
            except ValueError:
                # Default to a sensible type if the string doesn't match any enum
                from .utils import logger
                logger.warning(f"Unknown transaction type: {transaction_type}, defaulting to FEE")
                self.transaction_type = TransactionType.FEE
        else:
            self.transaction_type = transaction_type
            
        self.amount = amount
        self.description = description
        self.provider = provider
        
        # Increment the class-level counter
        Transaction.transaction_count += 1
    
    @property
    def type(self):
        """
        Property to access transaction_type as 'type'.
        This provides backward compatibility with code expecting a 'type' attribute.
        
        Returns:
            The transaction type enum
        """
        return self.transaction_type
        
    def __str__(self) -> str:
        """String representation of the transaction."""
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {self.description} ${self.amount:.2f}"
    
    @property
    def age(self) -> timedelta:
        """Calculate the age of the transaction."""
        return datetime.now() - self.timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert transaction to a dictionary for serialization.
        
        This method facilitates JSON serialization for storage or API communication.
        
        Returns:
            Dictionary representation of the transaction
        """
        return {
            'transaction_id': self.transaction_id,
            'timestamp': self.timestamp.isoformat(),
            'transaction_type': str(self.transaction_type),
            'amount': self.amount,
            'description': self.description,
            'provider': self.provider
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """
        Create a Transaction object from a dictionary.
        
        This class method acts as a factory, creating instances from serialized data.
        
        Args:
            data: Dictionary containing transaction data
            
        Returns:
            New Transaction instance
        """
        transaction = cls(
            transaction_type=data['transaction_type'],
            amount=data['amount'],
            description=data.get('description', ''),
            provider=data.get('provider', 'Default')
        )
        
        # Override automatically generated values
        transaction.timestamp = datetime.fromisoformat(data['timestamp'])
        transaction.transaction_id = data['transaction_id']
        
        return transaction


# Create a placeholder for BankingInterface for now 
# This will avoid circular import issues as BankingInterface is used by BankAccount
class BankingInterface(Protocol):
    """Interface that defines the core banking operations."""
    
    def deposit(self, amount: float, description: str = "") -> TransactionResult: ...
    
    def withdraw(self, amount: float, description: str = "") -> TransactionResult: ...

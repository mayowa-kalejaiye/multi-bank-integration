"""Utility functions and common configurations for the banking system."""
from __future__ import annotations
from datetime import datetime
import hashlib
import random
import logging
import threading
import functools
import contextlib
import json
import sys
from typing import Callable, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler('bank_system.log')]
)
logger = logging.getLogger('BankingSystem')

# Ensure proper encoding for emojis
sys.stdout.reconfigure(encoding='utf-8')

# Decorators for cross-cutting concerns
def transaction_logger(func: Callable) -> Callable:
    """
    Decorator to log all banking transactions.
    
    This demonstrates Python's decorator pattern for Aspect-Oriented Programming (AOP),
    adding transaction logging behavior to methods without modifying their core logic.
    
    Args:
        func: The function to be decorated
        
    Returns:
        Wrapped function with logging capability
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # The first argument (self) could be a BankAccount or another object
        obj = args[0]
        
        # Get the appropriate name for logging
        if hasattr(obj, 'name'):
            name = obj.name
        elif hasattr(obj, 'primary_account') and hasattr(obj.primary_account, 'name'):
            # For AccountLinking objects, use the primary account's name
            name = f"{obj.primary_account.name}'s account linking"
        else:
            # Generic fallback
            name = obj.__class__.__name__
        
        logger.info(f"TRANSACTION START: {name} is performing {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            logger.info(f"TRANSACTION SUCCESS: {name} completed {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"TRANSACTION FAILED: {name} failed {func.__name__} - {str(e)}")
            raise
            
    return wrapper


def retry(max_attempts: int = 3, delay_seconds: float = 1.0):
    """
    Decorator for automatic retry of operations that might fail temporarily.
    
    This demonstrates a parameterized decorator that takes arguments,
    showing how to create more flexible higher-order functions.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay_seconds: Delay between retry attempts
        
    Returns:
        Decorator function with the specified parameters
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(f"Attempt {attempt} failed, retrying in {delay_seconds}s: {str(e)}")
                        import time
                        time.sleep(delay_seconds)
            
            logger.error(f"All {max_attempts} attempts failed")
            raise last_exception
            
        return wrapper
    return decorator


# Context manager for transaction safety
@contextlib.contextmanager
def transaction_context(account):
    """
    Context manager to ensure transaction safety.
    
    This demonstrates Python's context manager protocol using the @contextmanager
    decorator. It provides a clean way to handle setup and teardown logic around
    a transaction, ensuring proper state management regardless of exceptions.
    
    Args:
        account: The account being operated on
        
    Yields:
        The account for use within the context
    """
    prev_state = (account.balance, account.savings)
    transaction_id = hashlib.md5(f"{account.account_id}{datetime.now()}".encode()).hexdigest()
    logger.info(f"Transaction {transaction_id} started for {account.name}")
    
    try:
        yield account
        logger.info(f"Transaction {transaction_id} completed successfully")
    except Exception as e:
        # Rollback on error
        account.balance, account.savings = prev_state
        logger.error(f"Transaction {transaction_id} failed, rolling back: {str(e)}")
        raise
    finally:
        logger.info(f"Transaction {transaction_id} finalized")


def generate_id(seed_data: str) -> str:
    """Generate a unique ID using SHA-256 hashing."""
    return hashlib.md5(f"{seed_data}{datetime.now()}".encode()).hexdigest()[:12]

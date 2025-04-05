"""AI-powered banking services."""
import random
from typing import List, Dict, ClassVar, Final

from .utils import logger, retry
from .models import Transaction


class AIServices:
    """Class for AI-powered banking services."""
    
    # Service status
    _service_status: ClassVar[str] = "operational"
    
    @staticmethod
    def fraud_detection(transaction_amount: float, account_avg: float = 100) -> bool:
        """Detect potentially fraudulent transactions based on amount."""
        threshold = account_avg * 3
        if transaction_amount > threshold:
            logger.warning(f"Potential fraud detected: ${transaction_amount:.2f} (threshold: ${threshold:.2f})")
            print("🚨 AI Alert: Suspicious transaction detected! Possible fraud.\n")
            return True
        return False
        
    @staticmethod
    def smart_budgeting(transaction_history: List[Transaction]) -> Dict[str, float]:
        """Perform AI-driven budget analysis on transaction history."""
        categories = {"food": 0, "entertainment": 0, "shopping": 0, "other": 0}
        
        # Analyze transactions
        for transaction in transaction_history:
            if "food" in transaction.description.lower():
                categories["food"] += transaction.amount
            elif "entertainment" in transaction.description.lower():
                categories["entertainment"] += transaction.amount
            elif "shop" in transaction.description.lower():
                categories["shopping"] += transaction.amount
            else:
                categories["other"] += transaction.amount
                
        print("📊 AI Smart Budgeting Analysis:")
        for category, amount in categories.items():
            print(f"💰 You spent ${amount:.2f} on {category} this month.")
        
        return categories
    
    @staticmethod
    @retry(max_attempts=3, delay_seconds=1.0)
    def predict_currency_conversion(from_currency: str, to_currency: str) -> float:
        """
        Get currency exchange rates with built-in retry logic.
        
        The @retry decorator demonstrates how to make external API calls more robust
        by automatically retrying on failure.
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Conversion rate
        """
        # Simulate a potential API failure
        if random.random() < 0.3:
            raise ConnectionError("Simulated API timeout")
            
        # In a real app, this would call an exchange rate API
        rates = {
            "USD_EUR": 0.92,
            "EUR_USD": 1.09,
            "USD_GBP": 0.79,
            "GBP_USD": 1.27
        }
        
        rate_key = f"{from_currency}_{to_currency}"
        if rate_key in rates:
            return rates[rate_key]
        else:
            # Return a simulated rate if pair not found
            return round(random.uniform(0.8, 1.2), 2)
    
    @classmethod
    def get_service_status(cls) -> str:
        """Check if AI services are operational."""
        return f"AI Services: {cls._service_status}"
    
    @classmethod
    def set_service_status(cls, status: str) -> None:
        """Update the service status."""
        cls._service_status = status
        logger.info(f"AI service status changed to: {status}")

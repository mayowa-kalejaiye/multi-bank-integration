"""Security management for banking system."""
from datetime import datetime
from typing import List, Dict, Optional, Any

from .utils import logger
from .models import SecurityException


class SecurityManager:
    """Class that handles security features of bank accounts."""
    
    def __init__(self, account):
        """Initialize with a reference to the account it's protecting."""
        self.account = account
        self._locked = False
        self._failed_attempts = 0
        self._last_access = datetime.now()
        self._security_log = []
    
    def check_operation_allowed(self, operation_name: str) -> None:
        """Check if a protected operation is allowed given the account state."""
        if self._locked:
            self._log_security_event(f"Blocked access to {operation_name} while account locked")
            raise SecurityException(f"Account is locked. Cannot perform {operation_name}")
    
    def _log_security_event(self, message: str):
        """Log a security-related event.""" 
        event = {
            'timestamp': datetime.now().isoformat(),
            'account_id': self.account.account_id,
            'message': message
        }
        self._security_log.append(event)
        logger.warning(f"SECURITY: {message} ({self.account.name})")
    
    @property
    def locked(self) -> bool:
        """Property to check if the account is locked."""
        return self._locked
    
    def lock_account(self) -> None:
        """Lock the account to prevent transactions."""
        self._locked = True
        self._log_security_event(f"Account locked")
        print(f"🔒 Account '{self.account.name}' is now LOCKED.\n")

    def unlock_account(self, verification_code: Optional[str] = None) -> bool:
        """Unlock the account to allow transactions."""
        # In a real system, we'd verify the code here
        valid_code = verification_code == "1234" or verification_code is None
        
        if valid_code:
            self._locked = False
            self._failed_attempts = 0
            self._log_security_event(f"Account unlocked successfully")
            print(f"🔓 Account '{self.account.name}' is now UNLOCKED.\n")
            return True
        else:
            self._failed_attempts += 1
            self._log_security_event(f"Failed unlock attempt ({self._failed_attempts})")
            
            if self._failed_attempts >= 3:
                self._log_security_event(f"Account locked due to too many failed attempts")
                print("⚠️ Too many failed attempts. Account locked for security.\n")
                
            return False
    
    def register_access(self) -> None:
        """Record a successful access to the account."""
        self._last_access = datetime.now()
        self._log_security_event(f"Successful account access")
    
    def record_failed_attempt(self) -> None:
        """Record a failed authentication attempt and lock if necessary."""
        self._failed_attempts += 1
        self._log_security_event(f"Failed authentication attempt ({self._failed_attempts})")
        
        if self._failed_attempts >= 3:
            self.lock_account()
            print("⚠️ Too many failed attempts. Account locked for security.\n")
    
    def get_security_log(self) -> List[Dict[str, Any]]:
        """Get the security event log."""
        return self._security_log.copy()

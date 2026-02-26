"""
Robust logging configuration for the trading ecosystem.
Ensures consistent log formatting and centralized log management.
"""
import logging
import sys
from datetime import datetime
from typing import Optional
import json
from dataclasses import dataclass, asdict

@dataclass
class LogEntry:
    """Structured log entry for Firestore storage."""
    timestamp: str
    level: str
    component: str
    message: str
    agent_id: Optional[str] = None
    strategy_id: Optional[str] = None
    trade_id: Optional[str] = None
    error_details: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for Firestore."""
        return asdict(self)

class EcosystemLogger:
    """Centralized logging system with Firestore integration."""
    
    def __init__(self, component_name: str, agent_id: Optional[str] = None):
        self.component_name = component_name
        self.agent_id = agent_id
        self.firestore_client = None
        
        # Set up console logging
        self.logger = logging.getLogger(component_name)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # Initialize Firestore client from config
        try:
            from config import config
            self.firestore_client = config.firestore_client
        except ImportError:
            pass
    
    def _log_to_firestore(self, level: str, message: str, **kwargs) -> None:
        """Send structured logs to Firestore."""
        if not self.firestore_client:
            return
            
        try:
            entry = LogEntry(
                timestamp=datetime.utcnow().isoformat(),
                level=level,
                component=self.component_name,
                message=message,
                agent_id=self.agent_id,
                **kwargs
            )
            
            # Store in Firestore
            collection = self.firestore_client.collection("ecosystem_logs")
            collection.add(entry.to_dict())
            
        except Exception as e:
            # Fallback to console if Firestore fails
            self.logger.error(f"Failed to log to Firestore: {e}")
    
    def info(self, message: str, **kwargs) -> None:
        """Log info level message."""
        self.logger.info(message)
        self._log_to_firestore("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning level message."""
        self.logger.warning(message)
        self._log_to_firestore("WARNING", message, **kwargs)
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs) -> None:
        """Log error level message with optional exception."""
        error_details = str(error) if error else None
        self.logger.error(f"{message}: {error_details}")
        self._log_to_firestore("ERROR", message, error_details=error_details, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
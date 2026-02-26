"""
Configuration management for Autonomous Trading Ecosystem Evolution Engine.
Centralizes environment variables, Firebase credentials, and system constants.
"""
import os
from dataclasses import dataclass
from typing import Optional
from enum import Enum
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import Client
import logging

class TradingMode(Enum):
    """Operation modes for the trading ecosystem."""
    PAPER = "paper"
    LIVE = "live"
    BACKTEST = "backtest"

@dataclass
class FirebaseConfig:
    """Firebase configuration container."""
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    token_uri: str = "https://oauth2.googleapis.com/token"
    
    @classmethod
    def from_env(cls) -> Optional['FirebaseConfig']:
        """Initialize from environment variables."""
        try:
            private_key = os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n')
            return cls(
                project_id=os.getenv("FIREBASE_PROJECT_ID", ""),
                private_key_id=os.getenv("FIREBASE_PRIVATE_KEY_ID", ""),
                private_key=private_key,
                client_email=os.getenv("FIREBASE_CLIENT_EMAIL", "")
            )
        except Exception as e:
            logging.error(f"Failed to load Firebase config: {e}")
            return None

class Config:
    """Main configuration class."""
    
    def __init__(self):
        self.mode = TradingMode(os.getenv("TRADING_MODE", "paper"))
        self.exchange_name = os.getenv("EXCHANGE_NAME", "binance")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.firebase_config = FirebaseConfig.from_env()
        self.firestore_client: Optional[Client] = None
        
        # Initialize Firebase if credentials available
        self._init_firebase()
        
    def _init_firebase(self) -> None:
        """Initialize Firebase Firestore client."""
        if not self.firebase_config or not self.firebase_config.project_id:
            logging.warning("Firebase credentials not found. Running in local mode.")
            return
            
        try:
            cred_dict = {
                "type": "service_account",
                "project_id": self.firebase_config.project_id,
                "private_key_id": self.firebase_config.private_key_id,
                "private_key": self.firebase_config.private_key,
                "client_email": self.firebase_config.client_email,
                "token_uri": self.firebase_config.token_uri
            }
            
            cred = credentials.Certificate(cred_dict)
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            
            self.firestore_client = firestore.client()
            logging.info("Firebase Firestore initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize Firebase: {e}")
            self.firestore_client = None

# Global configuration instance
config = Config()
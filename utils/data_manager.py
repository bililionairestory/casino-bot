import json
import os
import logging
from typing import Dict, Any, Optional, Union
import asyncio

logger = logging.getLogger(__name__)

class DataManager:
    """
    Handles data persistence for the gambling bot, storing user data in a JSON file.
    """
    
    def __init__(self, data_file: str = "user_data.json"):
        """
        Initialize the DataManager with the specified data file.
        
        Args:
            data_file (str): Name of the JSON file to store data
        """
        self.data_file = data_file
        self.data = {}
        self.default_balance = 500  # Starting balance for new users
        self.lock = asyncio.Lock()  # Lock for thread-safe file operations
        
        # Load data from file, create if doesn't exist
        self._load_data()
    
    def _load_data(self) -> None:
        """Load data from the JSON file, creating it if it doesn't exist."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
                logger.info(f"Loaded data for {len(self.data)} users")
            else:
                self.data = {}
                self._save_data()  # Create empty file
                logger.info(f"Created new data file: {self.data_file}")
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            self.data = {}
    
    def _save_data(self) -> None:
        """Save data to the JSON file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
            logger.debug("Data saved successfully")
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
    
    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Get a user's data, creating a new entry if the user doesn't exist.
        
        Args:
            user_id (str): Discord user ID
            
        Returns:
            Dict[str, Any]: User data dictionary
        """
        # Check if user exists, create default data if not
        if user_id not in self.data:
            self.data[user_id] = {
                "balance": self.default_balance,
                "stats": {
                    "slots_played": 0,
                    "slots_won": 0
                }
            }
            self._save_data()
        
        return self.data[user_id]
    
    def get_all_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all user data.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of all user data
        """
        return self.data
    
    def update_balance(self, user_id: str, amount: int) -> int:
        """
        Update a user's balance by adding or subtracting coins.
        
        Args:
            user_id (str): Discord user ID
            amount (int): Amount to add (positive) or subtract (negative)
            
        Returns:
            int: New balance
        """
        user_data = self.get_user_data(user_id)
        user_data["balance"] += amount
        
        # Ensure balance doesn't go negative
        if user_data["balance"] < 0:
            user_data["balance"] = 0
        
        self._save_data()
        return user_data["balance"]
    
    def update_stats(self, user_id: str, stat_name: str, value: Union[int, str]) -> None:
        """
        Update a user's stats.
        
        Args:
            user_id (str): Discord user ID
            stat_name (str): Name of the stat to update
            value (Union[int, str]): Value to add or set
        """
        user_data = self.get_user_data(user_id)
        
        # Make sure stats dict exists
        if "stats" not in user_data:
            user_data["stats"] = {}
        
        # For numeric values, add to existing value
        if isinstance(value, int) and stat_name in user_data["stats"] and isinstance(user_data["stats"][stat_name], int):
            user_data["stats"][stat_name] += value
        else:
            # Otherwise, set the value directly
            user_data["stats"][stat_name] = value
        
        self._save_data()
    
    def update_user_data(self, user_id: str, key: str, value: Any) -> None:
        """
        Update a specific field in a user's data.
        
        Args:
            user_id (str): Discord user ID
            key (str): Field name to update
            value (Any): Value to set
        """
        user_data = self.get_user_data(user_id)
        user_data[key] = value
        self._save_data()

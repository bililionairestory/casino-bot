import random
from typing import Dict, List, Any, Tuple

class SlotMachine:
    """
    Implements a slot machine game with configurable symbols, weights, and payouts.
    """
    
    def __init__(self):
        """Initialize the slot machine with symbols, weights, and payouts."""
        # Define symbols and their weights (probability)
        self.SYMBOLS = {
            "7️⃣": "Rare",     # Seven
            "💎": "Uncommon",  # Diamond
            "🎰": "Wild",      # Wild
            "*️⃣": "Scatter",   # Scatter
            "🔔": "Medium",    # Bell
            "🍊": "Common",    # Orange
            "🍋": "Common",    # Lemon
            "❤️": "Common",    # Heart
            "🍒": "Common"     # Cherry
        }
        
        # Symbol weights (higher = more likely)
        self.SYMBOL_WEIGHTS = {
            "7️⃣": 1,    # Rare
            "💎": 3,    # Uncommon
            "🎰": 5,    # Wild
            "*️⃣": 8,    # Scatter
            "🔔": 12,   # Medium
            "🍊": 18,   # Common
            "🍋": 20,   # Common
            "❤️": 22,   # Common
            "🍒": 25    # Most common
        }
        
        # Payout multipliers for matches
        self.PAYOUTS = {
            "7️⃣": {2: 25, 3: 500},   # 7s
            "💎": {2: 10, 3: 25},     # Diamond
            "🎰": {2: 3, 3: 5},       # Wild
            "*️⃣": {2: 2, 3: 3},       # Scatter
            "🔔": {2: 1, 3: 2},       # Bell
            "🍊": {2: 1, 3: 1},       # Orange
            "🍋": {2: 1, 3: 0.75},    # Lemon
            "❤️": {2: 0.75, 3: 0.5},  # Heart
            "🍒": {2: 0.25, 3: 0.5}   # Cherry
        }
        
        # Special rules for wilds and scatters
        self.WILD = "🎰"
        self.SCATTER = "*️⃣"
    
    def get_random_symbol(self) -> str:
        """
        Get a random symbol based on the defined weights.
        
        Returns:
            str: A randomly selected symbol
        """
        total_weight = sum(self.SYMBOL_WEIGHTS.values())
        random_val = random.random() * total_weight
        
        for symbol, weight in self.SYMBOL_WEIGHTS.items():
            random_val -= weight
            if random_val <= 0:
                return symbol
        
        # Fallback to most common symbol (cherry)
        return "🍒"
    
    def spin(self) -> Dict[str, Any]:
        """
        Spin the slot machine and calculate results.
        
        Returns:
            Dict[str, Any]: Dictionary containing symbols, multiplier, and matching pattern
        """
        # Generate 3 random symbols
        symbols = [self.get_random_symbol() for _ in range(3)]
        
        # Calculate winnings
        multiplier = self._calculate_payout(symbols)
        pattern = self._get_winning_pattern(symbols)
        
        return {
            "symbols": symbols,
            "multiplier": multiplier,
            "pattern": pattern
        }
    
    def _calculate_payout(self, symbols: List[str]) -> float:
        """
        Calculate the payout multiplier for a given set of symbols.
        
        Args:
            symbols (List[str]): List of 3 symbols
            
        Returns:
            float: Payout multiplier
        """
        # Count occurrences of each symbol
        counts = {}
        for symbol in self.SYMBOLS:
            # Regular symbols
            symbol_count = symbols.count(symbol)
            counts[symbol] = symbol_count
            
            # Count wilds as matching for non-scatter symbols
            if symbol != self.SCATTER:
                counts[symbol] += symbols.count(self.WILD)
        
        # Find the highest paying combination
        max_payout = 0
        
        for symbol, count in counts.items():
            # Minimum 2 matches for a win
            if count >= 2 and symbol in self.PAYOUTS:
                # Get the payout for exact count or highest available
                payout_table = self.PAYOUTS[symbol]
                payout = payout_table.get(count, 0)
                
                # Update max payout if this is better
                if payout > max_payout:
                    max_payout = payout
        
        return max_payout
    
    def _get_winning_pattern(self, symbols: List[str]) -> str:
        """
        Get a description of the winning pattern.
        
        Args:
            symbols (List[str]): List of 3 symbols
            
        Returns:
            str: Description of the winning pattern or empty string if no win
        """
        # Count occurrences of each symbol (including wilds as matches)
        counts = {}
        for symbol in self.SYMBOLS:
            # Regular symbols
            symbol_count = symbols.count(symbol)
            
            # Count wilds as matching for non-scatter symbols
            wild_count = 0
            if symbol != self.SCATTER:
                wild_count = symbols.count(self.WILD)
            
            total_count = symbol_count + wild_count
            if total_count >= 2:
                counts[symbol] = (total_count, symbol_count, wild_count)
        
        # Find the highest paying combination
        max_payout = 0
        winning_symbol = None
        winning_counts = None
        
        for symbol, count_data in counts.items():
            total_count, _, _ = count_data
            if symbol in self.PAYOUTS and total_count >= 2:
                payout = self.PAYOUTS[symbol].get(total_count, 0)
                if payout > max_payout:
                    max_payout = payout
                    winning_symbol = symbol
                    winning_counts = count_data
        
        # If no winning combination found
        if not winning_symbol or max_payout == 0:
            return ""
        
        # Create description of the winning pattern
        total_count, regular_count, wild_count = winning_counts
        
        if wild_count > 0:
            if winning_symbol == self.SCATTER:
                return f"{total_count}x {winning_symbol} (Scatter)"
            else:
                return f"{regular_count}x {winning_symbol} + {wild_count}x 🎰 (Wild)"
        else:
            special = ""
            if winning_symbol == self.WILD:
                special = " (Wild)"
            elif winning_symbol == self.SCATTER:
                special = " (Scatter)"
                
            return f"{total_count}x {winning_symbol}{special}"

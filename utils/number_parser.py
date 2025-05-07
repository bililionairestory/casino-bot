"""
Utility for parsing numerical inputs with suffixes (k, m, g, etc.)
"""

def parse_amount(amount_str):
    """
    Parse an amount string with potential suffix (k, m, g, etc.)
    
    Args:
        amount_str (str): The amount string to parse (e.g., "1k", "2.5m")
        
    Returns:
        int: The parsed amount or None if invalid
    """
    if not amount_str:
        return None
        
    # Convert to lowercase for case-insensitive matching
    amount_str = str(amount_str).lower().strip()
    
    # Define suffix multipliers
    suffixes = {
        'k': 1_000,                    # Thousand
        'm': 1_000_000,                # Million
        'g': 1_000_000_000,            # Billion
        't': 1_000_000_000_000,        # Trillion
        'p': 1_000_000_000_000_000,    # Quadrillion
        'e': 1_000_000_000_000_000_000, # Quintillion
        'z': 1_000_000_000_000_000_000_000, # Sextillion
        'y': 1_000_000_000_000_000_000_000_000 # Septillion
    }
    
    # Check if the input ends with a known suffix
    if len(amount_str) > 1 and amount_str[-1] in suffixes:
        suffix = amount_str[-1]
        numeric_part = amount_str[:-1]
        
        try:
            # Convert numeric part to float, then multiply by suffix value
            parsed_amount = float(numeric_part) * suffixes[suffix]
            return int(parsed_amount)  # Convert to integer
        except ValueError:
            return None  # Invalid numeric format
    
    # No suffix, try to parse as plain number
    try:
        return int(float(amount_str))  # Support decimal inputs
    except ValueError:
        return None  # Invalid numeric format
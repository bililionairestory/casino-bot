"""
Main entry point for the Discord gambling bot and web interface.
"""
import os

# Import the Flask app for gunicorn
from app import app

def main():
    """
    Main entry point for the Discord gambling bot.
    """
    from bot import setup_bot
    
    # Get Discord bot token from environment variable
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        raise ValueError("DISCORD_BOT_TOKEN environment variable not set")
    
    # Create and run the bot
    bot = setup_bot()
    bot.run(token)

if __name__ == "__main__":
    # Only run the bot when this script is executed directly
    main()
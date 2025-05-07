# Discord Gambling Bot

A Python-based Discord gambling bot with slot machine functionality and virtual currency management.

## Features

### Discord Bot
- **Economy System**: Virtual currency with daily rewards, balance checking, and transfers
- **Gambling Games**: Slot machine with different symbols and payouts
- **Leaderboards**: Track the richest users on your server
- **Number Suffix Support**: Use k, m, g, etc. for large numbers (e.g., 1k = 1,000)
- **Vote Multipliers**: Earn rewards for voting for the bot with special milestone multipliers

### Web Interface
- **User Accounts**: Register, login, and manage your account
- **Dashboard**: See your Discord bot stats on the web
- **How to Play Guide**: Learn about available games and commands
- **Leaderboards**: Web-based view of the richest gamblers

## Economy Commands

- `!balance` / `!bal` - Check your balance or another user's balance
- `!daily` - Claim your daily reward (100 coins)
- `!give <user> <amount>` - Give coins to another user
- `!leaderboard` / `!lb` - Show the server's gambling leaderboard
- `!vote <number>` - Claim your reward for voting for the bot
- `!votemultipliers` / `!vm` - Show vote multiplier tiers and rewards

## Gambling Commands

- `!slot <bet>` - Play the slot machine with a specified bet amount
- `!symbols` - Show slot machine symbols and their payouts
- `!odds` - Show information about slot machine odds

## Number Suffixes

You can use shorthand notations for large numbers:

| Suffix | Value              | Example |
|--------|-------------------|---------|
| k      | 1,000             | 1k = 1,000 |
| m      | 1,000,000         | 1m = 1,000,000 |
| g      | 1,000,000,000     | 1g = 1,000,000,000 |
| t      | 1,000,000,000,000 | 1t = 1,000,000,000,000 |
| p      | 10^15             | 1p = 1,000,000,000,000,000 |
| e      | 10^18             | 1e = 1,000,000,000,000,000,000 |
| z      | 10^21             | 1z = 1,000,000,000,000,000,000,000 |
| y      | 10^24             | 1y = 1,000,000,000,000,000,000,000,000 |

## Vote Multiplier System

Vote for the bot to earn rewards! The more you vote, the higher your multiplier.

| Vote Number Range | Multiplier | Reward     |
|-------------------|------------|------------|
| 1-20              | 1x         | 100,000    |
| 21                | 3x         | 300,000    |
| 22-41             | 2x         | 200,000    |
| 42                | 6x         | 600,000    |
| 43-62             | 3x         | 300,000    |
| 63                | 9x         | 900,000    |
| 64-83             | 4x         | 400,000    |
| 84                | 12x        | 1,200,000  |

Special milestone votes (21, 42, 63, 84) have increased multipliers!

## Getting Started

1. Add the bot to your Discord server
2. Use `!help` to see all available commands
3. Claim your first coins with `!daily`
4. Try your luck with `!slot <bet>`
5. Check the leaderboard with `!leaderboard`

## Web Interface

The web interface provides an alternative way to interact with the bot:

1. Register for an account on the website
2. Link your Discord account
3. View your stats and balance on the dashboard
4. Check the global leaderboard

## Setup for Development

1. Clone the repository
2. Set up a Discord bot token
3. Install dependencies with `pip install -r requirements.txt`
4. Run the bot with `python main.py`

## License

[MIT License](LICENSE)
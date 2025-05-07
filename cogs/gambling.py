import discord
from discord.ext import commands
import asyncio
import random
from utils.data_manager import DataManager
from utils.slot_machine import SlotMachine
from utils.number_parser import parse_amount

class Gambling(commands.Cog):
    """Gambling game commands for the bot."""
    
    def __init__(self, bot):
        self.bot = bot
        self.data_manager = DataManager()
        self.slot_machine = SlotMachine()
    
    @commands.command(name="slot", brief="Play the slot machine")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def slot(self, ctx, bet_str: str = None):
        """
        Play the slot machine with a specified bet amount.
        
        Args:
            bet_str (str, optional): Amount to bet (can use k, m, g etc. suffixes). Default: minimum bet
        """
        # Default minimum bet
        minimum_bet = 10
        
        # Parse the bet amount
        if bet_str is None:
            bet = minimum_bet
            await ctx.send(f"No bet specified. Using minimum bet of {minimum_bet} coins.")
        else:
            # Parse the bet with potential suffixes (k, m, g, etc.)
            bet = parse_amount(bet_str)
            
            # Check if the parsed amount is valid
            if bet is None:
                await ctx.send("❌ Invalid bet format. Please use a valid number. Example: 100, 1k, 2.5m")
                ctx.command.reset_cooldown(ctx)
                return
        
        # Check if bet is valid
        if bet < minimum_bet:
            await ctx.send(f"❌ Minimum bet is {minimum_bet} coins.")
            ctx.command.reset_cooldown(ctx)
            return
        
        # Get user balance
        user_id = str(ctx.author.id)
        user_data = self.data_manager.get_user_data(user_id)
        
        # Check if user has enough balance
        if user_data["balance"] < bet:
            await ctx.send(f"❌ You don't have enough coins! Your balance: {user_data['balance']} coins")
            ctx.command.reset_cooldown(ctx)
            return
        
        # Deduct bet from balance
        self.data_manager.update_balance(user_id, -bet)
        
        # Create initial message
        embed = discord.Embed(
            title="🎰 Slot Machine",
            description="Spinning...",
            color=0xF1C40F
        )
        embed.set_footer(text=f"Bet: {bet} coins | Balance: {user_data['balance'] - bet} coins")
        message = await ctx.send(embed=embed)
        
        # Animated spinning effect
        for _ in range(3):
            # Generate random symbols for animation
            symbols = [random.choice(list(self.slot_machine.SYMBOLS)) for _ in range(3)]
            symbols_display = " | ".join(symbols)
            
            embed.description = f"**[ {symbols_display} ]**"
            await message.edit(embed=embed)
            await asyncio.sleep(0.5)
        
        # Get actual slot results
        result = self.slot_machine.spin()
        symbols_display = " | ".join(result["symbols"])
        
        # Calculate winnings
        winnings = bet * result["multiplier"]
        
        # Update user balance with winnings
        if winnings > 0:
            self.data_manager.update_balance(user_id, winnings)
        
        # Update user statistics
        user_data = self.data_manager.get_user_data(user_id)
        self.data_manager.update_stats(user_id, "slots_played", 1)
        
        if winnings > 0:
            self.data_manager.update_stats(user_id, "slots_won", 1)
            if winnings > user_data.get("stats", {}).get("highest_win", 0):
                self.data_manager.update_stats(user_id, "highest_win", winnings)
        
        # Prepare result message
        embed = discord.Embed(color=0xF1C40F)
        embed.set_author(name=f"{ctx.author.display_name}'s Slot Machine", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        
        embed.description = f"**[ {symbols_display} ]**"
        
        if result["multiplier"] > 0:
            embed.add_field(name="Result", value=f"🎉 You won **{winnings}** coins! (x{result['multiplier']})", inline=False)
            embed.color = 0x2ECC71  # Green for win
        else:
            embed.add_field(name="Result", value="😢 You lost your bet.", inline=False)
            embed.color = 0xE74C3C  # Red for loss
        
        # Show win pattern if applicable
        if result["pattern"]:
            embed.add_field(name="Pattern", value=result["pattern"], inline=False)
        
        current_balance = user_data["balance"]
        embed.set_footer(text=f"Bet: {bet} coins | New Balance: {current_balance} coins")
        
        await message.edit(embed=embed)
    
    @commands.command(name="symbols", brief="Show slot machine symbols and payouts")
    async def symbols(self, ctx):
        """Display information about slot machine symbols and their payouts."""
        embed = discord.Embed(
            title="🎰 Slot Machine Symbols & Payouts",
            description="Here are all the slot machine symbols and their payouts:",
            color=0xF1C40F
        )
        
        # Add each symbol group to the embed
        embed.add_field(
            name="Rare - 7️⃣",
            value="3x = 500:1 payout\n2x = 25:1 payout",
            inline=True
        )
        
        embed.add_field(
            name="Uncommon - 💎",
            value="3x = 25:1 payout\n2x = 10:1 payout",
            inline=True
        )
        
        embed.add_field(
            name="Wild - 🎰",
            value="3x = 5:1 payout\n2x = 3:1 payout\nReplaces any symbol except Scatter",
            inline=True
        )
        
        embed.add_field(
            name="Scatter - *️⃣",
            value="3x = 3:1 payout\n2x = 2:1 payout\nCounts anywhere on the line",
            inline=True
        )
        
        embed.add_field(
            name="Medium - 🔔",
            value="3x = 2:1 payout\n2x = 1:1 payout",
            inline=True
        )
        
        embed.add_field(
            name="Common Symbols",
            value="🍊: 3x = 1:1, 2x = 1:1\n🍋: 3x = 0.75:1, 2x = 1:1\n❤️: 3x = 0.5:1, 2x = 0.75:1\n🍒: 3x = 0.5:1, 2x = 0.25:1",
            inline=True
        )
        
        embed.set_footer(text="Use !slot <bet> to play the slot machine")
        await ctx.send(embed=embed)
    
    @commands.command(name="odds", brief="Show slot machine odds")
    async def odds(self, ctx):
        """Display information about slot machine odds."""
        embed = discord.Embed(
            title="🎰 Slot Machine Odds",
            description="Here are the odds of winning in the slot machine:",
            color=0xF1C40F
        )
        
        # Get probability information
        weights = self.slot_machine.SYMBOL_WEIGHTS
        total_weight = sum(weights.values())
        
        # Calculate and display probabilities for each symbol
        symbol_probs = {}
        for symbol, weight in weights.items():
            prob = weight / total_weight * 100
            symbol_probs[symbol] = f"{prob:.2f}%"
        
        # Add probability fields
        embed.add_field(
            name="Symbol Probabilities",
            value="\n".join([f"{symbol}: {prob}" for symbol, prob in symbol_probs.items()]),
            inline=False
        )
        
        # Add general odds information
        embed.add_field(
            name="Win Rates",
            value="Any win: ~30%\nBreak-even or better: ~20%\nBig win (10x or more): ~1%",
            inline=False
        )
        
        embed.set_footer(text="The house always has an edge, but you might get lucky!")
        await ctx.send(embed=embed)

async def setup(bot):
    """Add the Gambling cog to the bot."""
    await bot.add_cog(Gambling(bot))

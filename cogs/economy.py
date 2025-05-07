import discord
from discord.ext import commands
import asyncio
import datetime
from utils.data_manager import DataManager
from utils.number_parser import parse_amount

class Economy(commands.Cog):
    """Economy management commands for the bot."""
    
    def __init__(self, bot):
        self.bot = bot
        self.data_manager = DataManager()
        self.daily_amount = 100  # Amount of coins given for daily reward
        
        # Vote multiplier configuration
        self.vote_multipliers = [
            {"range": (1, 20), "multiplier": 1, "reward": 100_000},
            {"range": (21, 21), "multiplier": 3, "reward": 300_000},
            {"range": (22, 41), "multiplier": 2, "reward": 200_000},
            {"range": (42, 42), "multiplier": 6, "reward": 600_000},
            {"range": (43, 62), "multiplier": 3, "reward": 300_000},
            {"range": (63, 63), "multiplier": 9, "reward": 900_000},
            {"range": (64, 83), "multiplier": 4, "reward": 400_000},
            {"range": (84, 84), "multiplier": 12, "reward": 1_200_000},
        ]
    
    @commands.command(name="balance", aliases=["bal"], brief="Check your balance")
    async def balance(self, ctx, member: discord.Member = None):
        """
        Check your balance or another user's balance.
        
        Args:
            member (discord.Member, optional): The member whose balance to check
        """
        # Default to command user if no member specified
        target = member or ctx.author
        user_id = str(target.id)
        
        # Get user data
        user_data = self.data_manager.get_user_data(user_id)
        
        # Create and send embed
        embed = discord.Embed(
            title=f"{target.display_name}'s Balance",
            description=f"💰 **{user_data['balance']}** coins",
            color=0x3498DB
        )
        
        # Include stats if available
        stats = user_data.get("stats", {})
        if stats:
            slots_played = stats.get("slots_played", 0)
            slots_won = stats.get("slots_won", 0)
            win_rate = (slots_won / slots_played * 100) if slots_played > 0 else 0
            
            stats_text = [
                f"🎰 Slots Played: {slots_played}",
                f"🏆 Slots Won: {slots_won}",
                f"📊 Win Rate: {win_rate:.1f}%"
            ]
            
            if "highest_win" in stats:
                stats_text.append(f"💎 Highest Win: {stats['highest_win']}")
                
            embed.add_field(
                name="Statistics",
                value="\n".join(stats_text),
                inline=False
            )
        
        # Add footer with timestamp
        embed.set_footer(text=f"Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if target.avatar:
            embed.set_thumbnail(url=target.avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="daily", brief="Collect daily reward")
    async def daily(self, ctx):
        """Collect your daily reward of coins."""
        user_id = str(ctx.author.id)
        user_data = self.data_manager.get_user_data(user_id)
        
        # Check if user has already claimed their daily reward
        last_daily = user_data.get("last_daily")
        now = datetime.datetime.now().timestamp()
        
        # Check if 24 hours have passed since last claim
        if last_daily and now - last_daily < 86400:  # 86400 seconds = 24 hours
            # Calculate time remaining
            time_left = 86400 - (now - last_daily)
            hours, remainder = divmod(int(time_left), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            # Format time string
            time_str = f"{hours}h {minutes}m {seconds}s"
            
            await ctx.send(f"❌ You've already claimed your daily reward! Try again in **{time_str}**.")
            return
        
        # Update user balance and last_daily timestamp
        self.data_manager.update_balance(user_id, self.daily_amount)
        self.data_manager.update_user_data(user_id, "last_daily", now)
        
        # Get updated balance
        user_data = self.data_manager.get_user_data(user_id)
        
        # Create and send embed
        embed = discord.Embed(
            title="Daily Reward Claimed!",
            description=f"You received 💰 **{self.daily_amount}** coins!",
            color=0x2ECC71
        )
        
        embed.add_field(
            name="New Balance",
            value=f"💰 **{user_data['balance']}** coins",
            inline=False
        )
        
        # Add streak system later
        embed.set_footer(text="Come back tomorrow for another reward!")
        
        if ctx.author.avatar:
            embed.set_thumbnail(url=ctx.author.avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="leaderboard", aliases=["lb"], brief="Show server leaderboard")
    async def leaderboard(self, ctx):
        """Display the server's gambling leaderboard."""
        # Get all users' data
        all_data = self.data_manager.get_all_data()
        
        # Filter users who are in this server and sort by balance
        server_members_ids = [str(member.id) for member in ctx.guild.members]
        server_data = {
            user_id: data for user_id, data in all_data.items() 
            if user_id in server_members_ids
        }
        
        # Sort by balance, highest first
        sorted_data = sorted(
            server_data.items(), 
            key=lambda x: x[1]["balance"], 
            reverse=True
        )
        
        # Limit to top 10
        top_users = sorted_data[:10]
        
        # Check if there's data to show
        if not top_users:
            await ctx.send("No leaderboard data available for this server yet!")
            return
        
        # Create embed
        embed = discord.Embed(
            title=f"🏆 {ctx.guild.name} Gambling Leaderboard",
            description="Top 10 richest gamblers in the server:",
            color=0xF1C40F
        )
        
        # Add leaderboard entries
        for index, (user_id, data) in enumerate(top_users, 1):
            # Try to get member from server
            member = ctx.guild.get_member(int(user_id))
            name = member.display_name if member else f"User {user_id}"
            
            # Medal for top 3
            medal = "🥇" if index == 1 else "🥈" if index == 2 else "🥉" if index == 3 else f"{index}."
            
            embed.add_field(
                name=f"{medal} {name}",
                value=f"💰 **{data['balance']}** coins",
                inline=False
            )
        
        # Set footer with timestamp
        embed.set_footer(text=f"Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Set server icon as thumbnail if available
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="vote", brief="Claim your vote reward")
    async def vote(self, ctx, vote_number: int):
        """
        Claim your reward for voting for the bot.
        
        Args:
            vote_number (int): Your current vote number
        """
        user_id = str(ctx.author.id)
        user_data = self.data_manager.get_user_data(user_id)
        
        # Check if vote number is valid
        if vote_number < 1:
            await ctx.send("❌ Invalid vote number. Please enter a positive number.")
            return
            
        # Check if vote has already been claimed
        claimed_votes = user_data.get("claimed_votes", [])
        if vote_number in claimed_votes:
            await ctx.send(f"❌ You've already claimed the reward for vote #{vote_number}!")
            return
            
        # Find applicable multiplier
        multiplier_data = None
        for data in self.vote_multipliers:
            min_vote, max_vote = data["range"]
            if min_vote <= vote_number <= max_vote:
                multiplier_data = data
                break
                
        if not multiplier_data:
            # Use the highest tier if the vote number exceeds our defined ranges
            multiplier_data = self.vote_multipliers[-1]
        
        # Add reward
        reward = multiplier_data["reward"]
        multiplier = multiplier_data["multiplier"]
        
        self.data_manager.update_balance(user_id, reward)
        
        # Mark vote as claimed
        if "claimed_votes" not in user_data:
            self.data_manager.update_user_data(user_id, "claimed_votes", [vote_number])
        else:
            claimed_votes.append(vote_number)
            self.data_manager.update_user_data(user_id, "claimed_votes", claimed_votes)
            
        # Get updated balance
        user_data = self.data_manager.get_user_data(user_id)
        
        # Create and send embed
        embed = discord.Embed(
            title="🗳️ Vote Reward Claimed!",
            description=f"Thank you for vote #{vote_number}!",
            color=0x9B59B6
        )
        
        embed.add_field(
            name="Reward Multiplier",
            value=f"**{multiplier}x** multiplier applied",
            inline=True
        )
        
        embed.add_field(
            name="Coins Received",
            value=f"💰 **{reward:,}** coins",
            inline=True
        )
        
        embed.add_field(
            name="New Balance",
            value=f"💰 **{user_data['balance']:,}** coins",
            inline=False
        )
        
        # Special message for milestone votes
        if vote_number in [21, 42, 63, 84]:
            embed.add_field(
                name="🎉 Milestone Vote!",
                value=f"Vote #{vote_number} is a special milestone with an increased multiplier!",
                inline=False
            )
            
        embed.set_footer(text="Thank you for supporting the bot!")
        
        if ctx.author.avatar:
            embed.set_thumbnail(url=ctx.author.avatar.url)
            
        await ctx.send(embed=embed)
    
    @commands.command(name="votemultipliers", aliases=["vm"], brief="Show vote multipliers")
    async def vote_multipliers(self, ctx):
        """Display the vote multiplier tiers and rewards."""
        embed = discord.Embed(
            title="🗳️ Vote Multiplier System",
            description="Vote for the bot to earn rewards! More votes = bigger multipliers.",
            color=0x9B59B6
        )
        
        # Add each multiplier tier to the embed
        for data in self.vote_multipliers:
            min_vote, max_vote = data["range"]
            multiplier = data["multiplier"]
            reward = data["reward"]
            
            if min_vote == max_vote:
                name = f"Vote #{min_vote}"
                special = " 🌟 Special milestone vote!" if min_vote in [21, 42, 63, 84] else ""
                value = f"**{multiplier}x** multiplier = **{reward:,}** coins{special}"
            else:
                name = f"Votes #{min_vote}-#{max_vote}"
                value = f"**{multiplier}x** multiplier = **{reward:,}** coins"
                
            embed.add_field(name=name, value=value, inline=False)
            
        embed.set_footer(text="Use !vote <number> to claim your reward")
        await ctx.send(embed=embed)
    
    @commands.command(name="give", brief="Give coins to another user")
    async def give(self, ctx, member: discord.Member, amount: str):
        """
        Give some of your coins to another user.
        
        Args:
            member (discord.Member): The member to give coins to
            amount (str): Amount of coins to give (can use k, m, g, etc. suffixes)
        """
        # Parse the amount with potential suffixes (k, m, g, etc.)
        parsed_amount = parse_amount(amount)
        
        # Check for valid inputs
        if member.bot:
            await ctx.send("❌ You cannot give coins to bots!")
            return
            
        if parsed_amount is None:
            await ctx.send("❌ Invalid amount format. Please use a valid number. Example: 1000, 1k, 1.5m")
            return
            
        if parsed_amount <= 0:
            await ctx.send("❌ Amount must be positive!")
            return
        
        if member.id == ctx.author.id:
            await ctx.send("❌ You cannot give coins to yourself!")
            return
        
        # Get user data
        sender_id = str(ctx.author.id)
        receiver_id = str(member.id)
        
        sender_data = self.data_manager.get_user_data(sender_id)
        
        # Check if sender has enough balance
        if sender_data["balance"] < parsed_amount:
            await ctx.send(f"❌ You don't have enough coins! Your balance: {sender_data['balance']} coins")
            return
        
        # Format amount for display
        formatted_amount = f"{parsed_amount:,}"
        
        # Confirm transaction
        confirmation_msg = await ctx.send(f"Are you sure you want to give {formatted_amount} coins to {member.mention}? (yes/no)")
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["yes", "no"]
        
        try:
            response = await self.bot.wait_for("message", check=check, timeout=30.0)
        except asyncio.TimeoutError:
            await confirmation_msg.edit(content="❌ Transaction cancelled due to timeout.")
            return
        
        if response.content.lower() != "yes":
            await ctx.send("❌ Transaction cancelled.")
            return
        
        # Process transaction
        self.data_manager.update_balance(sender_id, -parsed_amount)
        self.data_manager.update_balance(receiver_id, parsed_amount)
        
        # Get updated balances
        sender_data = self.data_manager.get_user_data(sender_id)
        receiver_data = self.data_manager.get_user_data(receiver_id)
        
        # Create and send confirmation embed
        embed = discord.Embed(
            title="Transaction Complete",
            description=f"{ctx.author.mention} gave {member.mention} 💰 **{formatted_amount}** coins!",
            color=0x2ECC71
        )
        
        embed.add_field(
            name=f"{ctx.author.display_name}'s New Balance",
            value=f"💰 **{sender_data['balance']}** coins",
            inline=True
        )
        
        embed.add_field(
            name=f"{member.display_name}'s New Balance",
            value=f"💰 **{receiver_data['balance']}** coins",
            inline=True
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    """Add the Economy cog to the bot."""
    await bot.add_cog(Economy(bot))

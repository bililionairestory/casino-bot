import discord
from discord.ext import commands
import logging
import os
import asyncio

logger = logging.getLogger(__name__)

def setup_bot():
    """
    Configure and set up the Discord bot with necessary settings and cogs.
    
    Returns:
        discord.ext.commands.Bot: The configured bot instance
    """
    # Set up intents (privileges for the bot)
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    
    # Create bot instance with command prefix '!' and configured intents
    bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
    
    @bot.event
    async def on_ready():
        """Event triggered when the bot is ready and connected to Discord."""
        logger.info(f'Bot is online and logged in as {bot.user.name}')
        
        # Set the bot's activity/status
        await bot.change_presence(activity=discord.Game(name="!help for commands"))
        
        print(f"Bot is online as {bot.user.name}")
    
    @bot.event
    async def on_command_error(ctx, error):
        """Global error handler for bot commands."""
        if isinstance(error, commands.CommandOnCooldown):
            # Handle cooldown errors
            cooldown = round(error.retry_after, 2)
            await ctx.send(f"⏰ Slow down! Try again in {cooldown} seconds.")
            
        elif isinstance(error, commands.MissingRequiredArgument):
            # Handle missing arguments
            await ctx.send(f"❌ Missing required argument: {error.param.name}. Use !help for command usage.")
            
        elif isinstance(error, commands.BadArgument):
            # Handle bad arguments (type conversion errors)
            await ctx.send("❌ Invalid argument provided. Please check your input and try again.")
            
        elif isinstance(error, commands.CommandNotFound):
            # Ignore command not found errors
            pass
            
        else:
            # Log unexpected errors
            logger.error(f"Command error in {ctx.command}: {error}")
            await ctx.send("❌ An unexpected error occurred. Please try again later.")
    
    # Load cogs (extensions)
    async def load_extensions():
        """Load all cog extensions."""
        await bot.load_extension("cogs.gambling")
        await bot.load_extension("cogs.economy")
        logger.info("All extensions loaded successfully")
    
    # Setup hook to load extensions when the bot starts
    @bot.event
    async def setup_hook():
        await load_extensions()
    
    # Add a simple ping command
    @bot.command(name="ping", brief="Check if bot is responsive")
    async def ping(ctx):
        """Check the bot's response time."""
        latency = round(bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Bot latency: {latency}ms")
    
    # Custom help command
    @bot.command(name="help", brief="Shows help information")
    async def help_command(ctx, command_name=None):
        """
        Display help information for available commands.
        
        Args:
            command_name (str, optional): Specific command to get help for
        """
        embed = discord.Embed(
            title="🎰 Gambling Bot Help",
            description="Here are the available commands:",
            color=0x7289DA
        )
        
        if command_name:
            # Show help for specific command
            command = bot.get_command(command_name)
            if command:
                embed.add_field(
                    name=f"!{command.name}",
                    value=command.help or "No description available",
                    inline=False
                )
                embed.add_field(
                    name="Usage",
                    value=f"!{command.name} {command.signature}",
                    inline=False
                )
                if isinstance(command, commands.Command) and command._buckets._cooldown:
                    cooldown = command._buckets._cooldown
                    embed.add_field(
                        name="Cooldown",
                        value=f"{cooldown.rate} uses every {cooldown.per} seconds",
                        inline=False
                    )
            else:
                embed.description = f"Command '{command_name}' not found."
        else:
            # Show general help
            gambling_commands = []
            economy_commands = []
            other_commands = []
            
            for command in bot.commands:
                cmd_info = f"**!{command.name}** - {command.brief or 'No description'}"
                
                if command.cog_name == "Gambling":
                    gambling_commands.append(cmd_info)
                elif command.cog_name == "Economy":
                    economy_commands.append(cmd_info)
                else:
                    other_commands.append(cmd_info)
            
            if gambling_commands:
                embed.add_field(
                    name="🎲 Gambling Commands",
                    value="\n".join(gambling_commands),
                    inline=False
                )
            
            if economy_commands:
                embed.add_field(
                    name="💰 Economy Commands",
                    value="\n".join(economy_commands),
                    inline=False
                )
            
            if other_commands:
                embed.add_field(
                    name="🔧 Other Commands",
                    value="\n".join(other_commands),
                    inline=False
                )
                
            embed.add_field(
                name="ℹ️ Detailed Help",
                value="Use `!help <command>` for more information about a specific command.",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    return bot

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import traceback
from pathlib import Path
from utils.logger import bot_logger
import platform
from datetime import datetime

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
LOG_CHANNEL = int(os.getenv('LOG_CHANNEL_ID'))

# Setup bot intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True

class ModBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=None,  # No prefix needed for slash commands
            intents=intents,
            help_command=None,  # We'll implement our own help command
        )
        self.log_channel = None

    async def setup_hook(self):
        """Setup hook that runs when the bot starts."""
        # Log system startup
        bot_logger.system(
            "Bot is starting up",
            operation="startup"
        )

        # Load all cogs
        await self.load_cogs()
        
        # Sync slash commands
        bot_logger.system("Syncing slash commands...", operation="sync_commands")
        try:
            synced = await self.tree.sync()
            bot_logger.system(
                f"Successfully synced {len(synced)} commands",
                operation="sync_commands"
            )
        except Exception as e:
            bot_logger.system(
                "Failed to sync commands",
                operation="sync_commands",
                error=e
            )
            
    async def load_cogs(self):
        """Load all cogs from the cogs directory."""
        cogs_dir = Path('./cogs')
        for cog_file in cogs_dir.glob('*.py'):
            if cog_file.name != '__init__.py':
                try:
                    await self.load_extension(f'cogs.{cog_file.stem}')
                    bot_logger.system(
                        f"Loaded cog: {cog_file.stem}",
                        operation="load_cog"
                    )
                except Exception as e:
                    bot_logger.system(
                        f"Failed to load cog {cog_file.stem}",
                        operation="load_cog",
                        error=e
                    )

    async def on_ready(self):
        """Event that runs when the bot is ready."""
        bot_logger.event(
            "bot_ready",
            details={
                "bot_name": self.user.name,
                "bot_id": self.user.id,
                "guild_count": len(self.guilds),
                "startup_latency": round(self.latency * 1000, 2)
            }
        )

        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching,
            name='the server'
        ))
        
        # Set up logging channel
        self.log_channel = self.get_channel(LOG_CHANNEL)
        if not self.log_channel:
            bot_logger.system(
                "Log channel not found!",
                operation="setup_log_channel"
            )

    async def on_command_error(self, ctx, error):
        """Global error handler for commands."""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command!")
            bot_logger.command(
                ctx.command.name if ctx.command else "Unknown",
                str(ctx.author),
                ctx.guild.name if ctx.guild else "DM",
                status="permission_denied",
                error=error
            )
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I don't have permission to do that!")
            bot_logger.command(
                ctx.command.name if ctx.command else "Unknown",
                str(ctx.author),
                ctx.guild.name if ctx.guild else "DM",
                status="bot_permission_denied",
                error=error
            )
        elif isinstance(error, commands.MissingRole):
            await ctx.send("You don't have the required role to use this command!")
            bot_logger.command(
                ctx.command.name if ctx.command else "Unknown",
                str(ctx.author),
                ctx.guild.name if ctx.guild else "DM",
                status="role_denied",
                error=error
            )
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown. Try again in {error.retry_after:.2f}s")
            bot_logger.command(
                ctx.command.name if ctx.command else "Unknown",
                str(ctx.author),
                ctx.guild.name if ctx.guild else "DM",
                status="cooldown",
                error=error
            )
        else:
            await ctx.send(f"An error occurred: {str(error)}")
            bot_logger.command(
                ctx.command.name if ctx.command else "Unknown",
                str(ctx.author),
                ctx.guild.name if ctx.guild else "DM",
                status="error",
                error=error
            )
            
            if self.log_channel:
                await self.log_channel.send(
                    f"Error in command {ctx.command}:\n```py\n{traceback.format_exc()}```"
                )

    async def on_guild_join(self, guild):
        """Log when bot joins a new guild."""
        bot_logger.event(
            "guild_join",
            details={
                "guild_name": guild.name,
                "guild_id": guild.id,
                "member_count": guild.member_count,
                "owner": str(guild.owner)
            }
        )

    async def on_guild_remove(self, guild):
        """Log when bot leaves a guild."""
        bot_logger.event(
            "guild_remove",
            details={
                "guild_name": guild.name,
                "guild_id": guild.id
            }
        )

async def main():
    """Main function to start the bot."""
    async with ModBot() as bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        bot_logger.system("Bot shutdown initiated by user", operation="shutdown")
    except Exception as e:
        bot_logger.system("Bot crashed", operation="crash", error=e)
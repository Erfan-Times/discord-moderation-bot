import discord
from discord.ext import commands
from discord import app_commands
import re
from datetime import datetime, timedelta
from typing import Optional
import asyncio
from collections import defaultdict

class MessageMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Track message counts for anti-spam
        self.message_counts = defaultdict(lambda: defaultdict(int))
        self.spam_check_task = self.bot.loop.create_task(self.clear_message_counts())
        # Configurable settings - could be moved to a config file
        self.spam_threshold = 5  # messages
        self.spam_interval = 5   # seconds
        # Regex patterns for filtered content
        self.filter_patterns = [
            (re.compile(r'discord\.gg/[a-zA-Z0-9]+'), 'server invites'),
            (re.compile(r'(?:https?://)?(?:www\.)?(?:discord\.(?:gg|io|me|li)|discordapp\.com/invite)/[a-zA-Z0-9]+'), 'invite links'),
            (re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+'), 'links'),
            # Add more patterns as needed
        ]

    def cog_unload(self):
        """Cleanup when cog is unloaded."""
        self.spam_check_task.cancel()

    async def clear_message_counts(self):
        """Periodically clear message counts for spam detection."""
        while True:
            await asyncio.sleep(self.spam_interval)
            self.message_counts.clear()

    @app_commands.command(name="purge")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(
        amount="Number of messages to delete (1-100)",
        user="Only delete messages from this user",
        contains="Only delete messages containing this text"
    )
    async def purge(
        self,
        interaction: discord.Interaction,
        amount: app_commands.Range[int, 1, 100],
        user: Optional[discord.Member] = None,
        contains: Optional[str] = None
    ):
        """Delete a specified number of messages from the channel."""
        await interaction.response.defer(ephemeral=True)
        
        def check_message(message):
            if user and message.author != user:
                return False
            if contains and contains.lower() not in message.content.lower():
                return False
            return True

        try:
            deleted = await interaction.channel.purge(
                limit=amount,
                check=check_message,
                before=interaction.created_at
            )
            
            await interaction.followup.send(
                f"✅ Deleted {len(deleted)} messages.",
                ephemeral=True
            )
            
            # Log the action
            if self.bot.log_channel:
                embed = discord.Embed(
                    title="Messages Purged",
                    description=f"**Moderator:** {interaction.user.mention}\n"
                              f"**Channel:** {interaction.channel.mention}\n"
                              f"**Amount:** {len(deleted)} messages\n"
                              f"**User Filter:** {user.mention if user else 'None'}\n"
                              f"**Content Filter:** {contains if contains else 'None'}",
                    color=discord.Color.blue(),
                    timestamp=datetime.utcnow()
                )
                await self.bot.log_channel.send(embed=embed)
                
        except discord.Forbidden:
            await interaction.followup.send(
                "I don't have permission to delete messages in this channel.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f"An error occurred while deleting messages: {str(e)}",
                ephemeral=True
            )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handle message filtering and anti-spam."""
        if message.author.bot or isinstance(message.channel, discord.DMChannel):
            return

        # Check for spam
        author_id = message.author.id
        channel_id = message.channel.id
        self.message_counts[author_id][channel_id] += 1
        
        if self.message_counts[author_id][channel_id] >= self.spam_threshold:
            try:
                # Timeout the user for spam
                duration = timedelta(minutes=5)
                await message.author.timeout(duration, reason="Automatic timeout for spam")
                await message.channel.send(
                    f"{message.author.mention} has been timed out for spamming.",
                    delete_after=10
                )
                
                # Log the action
                if self.bot.log_channel:
                    embed = discord.Embed(
                        title="Auto-Timeout for Spam",
                        description=f"**User:** {message.author.mention} ({message.author.id})\n"
                                  f"**Channel:** {message.channel.mention}\n"
                                  f"**Duration:** 5 minutes",
                        color=discord.Color.orange(),
                        timestamp=datetime.utcnow()
                    )
                    await self.bot.log_channel.send(embed=embed)
                    
            except discord.Forbidden:
                pass  # Bot doesn't have permission to timeout
                
            # Clear the user's message count
            self.message_counts[author_id][channel_id] = 0

        # Check filtered content
        if not message.author.guild_permissions.manage_messages:
            content = message.content.lower()
            for pattern, filter_type in self.filter_patterns:
                if pattern.search(content):
                    try:
                        await message.delete()
                        warning = await message.channel.send(
                            f"{message.author.mention} Your message was removed for containing {filter_type}.",
                            delete_after=5
                        )
                        
                        # Log the action
                        if self.bot.log_channel:
                            embed = discord.Embed(
                                title="Message Filtered",
                                description=f"**User:** {message.author.mention} ({message.author.id})\n"
                                          f"**Channel:** {message.channel.mention}\n"
                                          f"**Filter Type:** {filter_type}\n"
                                          f"**Content:** ```{message.content}```",
                                color=discord.Color.yellow(),
                                timestamp=datetime.utcnow()
                            )
                            await self.bot.log_channel.send(embed=embed)
                            
                        break
                    except discord.Forbidden:
                        pass  # Bot doesn't have permission to delete messages

async def setup(bot):
    await bot.add_cog(MessageMod(bot))
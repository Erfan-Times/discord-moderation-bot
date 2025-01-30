import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from utils.logger import bot_logger

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kick")
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.describe(
        member="The member to kick",
        reason="The reason for kicking the member"
    )
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = "No reason provided"
    ):
        """Kick a member from the server."""
        # Log command initiation
        bot_logger.command(
            "kick",
            str(interaction.user),
            interaction.guild.name,
            status="started",
            details={
                "target_user": str(member),
                "target_id": member.id,
                "reason": reason
            }
        )

        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message(
                "You cannot kick this member as their role is higher or equal to yours.",
                ephemeral=True
            )
            bot_logger.command(
                "kick",
                str(interaction.user),
                interaction.guild.name,
                status="failed",
                details={"error": "Target user has higher or equal role"}
            )
            return

        # Create confirmation button
        confirm = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.danger)
        cancel = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary)
        view = discord.ui.View(timeout=30)
        view.add_item(confirm)
        view.add_item(cancel)

        async def confirm_callback(button_interaction):
            if button_interaction.user != interaction.user:
                await button_interaction.response.send_message(
                    "You cannot use this button.", ephemeral=True
                )
                return

            try:
                await member.kick(reason=f"{reason} - By {interaction.user}")
                await button_interaction.response.edit_message(
                    content=f"✅ Kicked {member.mention} | Reason: {reason}",
                    view=None
                )
                
                # Log successful kick
                bot_logger.command(
                    "kick",
                    str(interaction.user),
                    interaction.guild.name,
                    status="completed",
                    details={
                        "target_user": str(member),
                        "target_id": member.id,
                        "reason": reason
                    }
                )

                # Log audit
                bot_logger.audit(
                    "kick",
                    str(interaction.user),
                    str(member),
                    details={
                        "reason": reason,
                        "guild": interaction.guild.name
                    }
                )
                
                # Discord audit log
                if self.bot.log_channel:
                    embed = discord.Embed(
                        title="Member Kicked",
                        description=f"**Member:** {member.mention} ({member.id})\n"
                                  f"**Moderator:** {interaction.user.mention}\n"
                                  f"**Reason:** {reason}",
                        color=discord.Color.red(),
                        timestamp=datetime.utcnow()
                    )
                    await self.bot.log_channel.send(embed=embed)
                    
            except discord.Forbidden as e:
                await button_interaction.response.edit_message(
                    content="I don't have permission to kick that member.",
                    view=None
                )
                bot_logger.command(
                    "kick",
                    str(interaction.user),
                    interaction.guild.name,
                    status="error",
                    error=e
                )

        async def cancel_callback(button_interaction):
            if button_interaction.user != interaction.user:
                await button_interaction.response.send_message(
                    "You cannot use this button.", ephemeral=True
                )
                return
            
            await button_interaction.response.edit_message(
                content="❌ Kick cancelled.",
                view=None
            )
            bot_logger.command(
                "kick",
                str(interaction.user),
                interaction.guild.name,
                status="cancelled",
                details={
                    "target_user": str(member),
                    "target_id": member.id
                }
            )

        confirm.callback = confirm_callback
        cancel.callback = cancel_callback

        await interaction.response.send_message(
            f"Are you sure you want to kick {member.mention}?",
            view=view,
            ephemeral=True
        )

    @app_commands.command(name="ban")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(
        member="The member to ban",
        reason="The reason for banning the member",
        delete_messages="Number of days of messages to delete (0-7)"
    )
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = "No reason provided",
        delete_messages: app_commands.Range[int, 0, 7] = 0
    ):
        """Ban a member from the server."""
        # Log command initiation
        bot_logger.command(
            "ban",
            str(interaction.user),
            interaction.guild.name,
            status="started",
            details={
                "target_user": str(member),
                "target_id": member.id,
                "reason": reason,
                "delete_messages_days": delete_messages
            }
        )

        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message(
                "You cannot ban this member as their role is higher or equal to yours.",
                ephemeral=True
            )
            bot_logger.command(
                "ban",
                str(interaction.user),
                interaction.guild.name,
                status="failed",
                details={"error": "Target user has higher or equal role"}
            )
            return

        confirm = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.danger)
        cancel = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary)
        view = discord.ui.View(timeout=30)
        view.add_item(confirm)
        view.add_item(cancel)

        async def confirm_callback(button_interaction):
            if button_interaction.user != interaction.user:
                await button_interaction.response.send_message(
                    "You cannot use this button.", ephemeral=True
                )
                return

            try:
                await member.ban(
                    reason=f"{reason} - By {interaction.user}",
                    delete_message_days=delete_messages
                )
                await button_interaction.response.edit_message(
                    content=f"✅ Banned {member.mention} | Reason: {reason}",
                    view=None
                )

                # Log successful ban
                bot_logger.command(
                    "ban",
                    str(interaction.user),
                    interaction.guild.name,
                    status="completed",
                    details={
                        "target_user": str(member),
                        "target_id": member.id,
                        "reason": reason,
                        "delete_messages_days": delete_messages
                    }
                )

                # Log audit
                bot_logger.audit(
                    "ban",
                    str(interaction.user),
                    str(member),
                    details={
                        "reason": reason,
                        "delete_messages_days": delete_messages,
                        "guild": interaction.guild.name
                    }
                )
                
                # Discord audit log
                if self.bot.log_channel:
                    embed = discord.Embed(
                        title="Member Banned",
                        description=f"**Member:** {member.mention} ({member.id})\n"
                                  f"**Moderator:** {interaction.user.mention}\n"
                                  f"**Reason:** {reason}\n"
                                  f"**Message Delete Days:** {delete_messages}",
                        color=discord.Color.dark_red(),
                        timestamp=datetime.utcnow()
                    )
                    await self.bot.log_channel.send(embed=embed)
                    
            except discord.Forbidden as e:
                await button_interaction.response.edit_message(
                    content="I don't have permission to ban that member.",
                    view=None
                )
                bot_logger.command(
                    "ban",
                    str(interaction.user),
                    interaction.guild.name,
                    status="error",
                    error=e
                )

        async def cancel_callback(button_interaction):
            if button_interaction.user != interaction.user:
                await button_interaction.response.send_message(
                    "You cannot use this button.", ephemeral=True
                )
                return
            
            await button_interaction.response.edit_message(
                content="❌ Ban cancelled.",
                view=None
            )
            bot_logger.command(
                "ban",
                str(interaction.user),
                interaction.guild.name,
                status="cancelled",
                details={
                    "target_user": str(member),
                    "target_id": member.id
                }
            )

        confirm.callback = confirm_callback
        cancel.callback = cancel_callback

        await interaction.response.send_message(
            f"Are you sure you want to ban {member.mention}?",
            view=view,
            ephemeral=True
        )

    @app_commands.command(name="timeout")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.describe(
        member="The member to timeout",
        duration="Duration in minutes",
        reason="The reason for the timeout"
    )
    async def timeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        duration: app_commands.Range[int, 1, 40320],  # Max 28 days
        reason: Optional[str] = "No reason provided"
    ):
        """Timeout a member for a specified duration."""
        # Log command initiation
        bot_logger.command(
            "timeout",
            str(interaction.user),
            interaction.guild.name,
            status="started",
            details={
                "target_user": str(member),
                "target_id": member.id,
                "duration": duration,
                "reason": reason
            }
        )

        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message(
                "You cannot timeout this member as their role is higher or equal to yours.",
                ephemeral=True
            )
            bot_logger.command(
                "timeout",
                str(interaction.user),
                interaction.guild.name,
                status="failed",
                details={"error": "Target user has higher or equal role"}
            )
            return

        try:
            # Convert minutes to timedelta
            timeout_duration = timedelta(minutes=duration)
            await member.timeout(timeout_duration, reason=f"{reason} - By {interaction.user}")
            
            await interaction.response.send_message(
                f"✅ {member.mention} has been timed out for {duration} minutes | Reason: {reason}",
                ephemeral=True
            )

            # Log successful timeout
            bot_logger.command(
                "timeout",
                str(interaction.user),
                interaction.guild.name,
                status="completed",
                details={
                    "target_user": str(member),
                    "target_id": member.id,
                    "duration": duration,
                    "reason": reason
                }
            )

            # Log audit
            bot_logger.audit(
                "timeout",
                str(interaction.user),
                str(member),
                details={
                    "duration": duration,
                    "reason": reason,
                    "guild": interaction.guild.name
                }
            )
            
            # Discord audit log
            if self.bot.log_channel:
                embed = discord.Embed(
                    title="Member Timed Out",
                    description=f"**Member:** {member.mention} ({member.id})\n"
                              f"**Moderator:** {interaction.user.mention}\n"
                              f"**Duration:** {duration} minutes\n"
                              f"**Reason:** {reason}",
                    color=discord.Color.orange(),
                    timestamp=datetime.utcnow()
                )
                await self.bot.log_channel.send(embed=embed)
                
        except discord.Forbidden as e:
            await interaction.response.send_message(
                "I don't have permission to timeout that member.",
                ephemeral=True
            )
            bot_logger.command(
                "timeout",
                str(interaction.user),
                interaction.guild.name,
                status="error",
                error=e
            )

async def setup(bot):
    await bot.add_cog(Moderation(bot))
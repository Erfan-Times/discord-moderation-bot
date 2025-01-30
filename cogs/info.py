import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from typing import Optional
from collections import defaultdict

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Store warnings in memory (use a database in production)
        self.warnings = defaultdict(list)

    @app_commands.command(name="warn")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.describe(
        member="The member to warn",
        reason="The reason for the warning"
    )
    async def warn(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str
    ):
        """Add a warning to a user."""
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message(
                "You cannot warn this member as their role is higher or equal to yours.",
                ephemeral=True
            )
            return

        warning = {
            'reason': reason,
            'moderator_id': interaction.user.id,
            'timestamp': datetime.utcnow()
        }
        
        self.warnings[member.id].append(warning)
        
        # Notify the user
        try:
            await member.send(
                f"You have received a warning in {interaction.guild.name}\n"
                f"Reason: {reason}"
            )
        except discord.Forbidden:
            pass  # Cannot DM the user

        await interaction.response.send_message(
            f"✅ Warning added for {member.mention}\nReason: {reason}",
            ephemeral=True
        )

        # Log the warning
        if self.bot.log_channel:
            embed = discord.Embed(
                title="Member Warned",
                description=f"**Member:** {member.mention} ({member.id})\n"
                          f"**Moderator:** {interaction.user.mention}\n"
                          f"**Reason:** {reason}\n"
                          f"**Total Warnings:** {len(self.warnings[member.id])}",
                color=discord.Color.yellow(),
                timestamp=datetime.utcnow()
            )
            await self.bot.log_channel.send(embed=embed)

    @app_commands.command(name="warnings")
    @app_commands.describe(member="The member to check warnings for")
    async def warnings(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):
        """View warnings for a user."""
        if not self.warnings[member.id]:
            await interaction.response.send_message(
                f"{member.mention} has no warnings.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"Warnings for {member.display_name}",
            color=discord.Color.yellow()
        )

        for i, warning in enumerate(self.warnings[member.id], 1):
            moderator = interaction.guild.get_member(warning['moderator_id'])
            mod_name = moderator.mention if moderator else "Unknown Moderator"
            
            embed.add_field(
                name=f"Warning {i}",
                value=f"**Reason:** {warning['reason']}\n"
                      f"**Moderator:** {mod_name}\n"
                      f"**Date:** <t:{int(warning['timestamp'].timestamp())}:R>",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="clearwarnings")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.describe(member="The member to clear warnings for")
    async def clearwarnings(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):
        """Clear all warnings for a user."""
        if not self.warnings[member.id]:
            await interaction.response.send_message(
                f"{member.mention} has no warnings to clear.",
                ephemeral=True
            )
            return

        warning_count = len(self.warnings[member.id])
        self.warnings[member.id].clear()
        
        await interaction.response.send_message(
            f"✅ Cleared {warning_count} warnings for {member.mention}",
            ephemeral=True
        )

        # Log the action
        if self.bot.log_channel:
            embed = discord.Embed(
                title="Warnings Cleared",
                description=f"**Member:** {member.mention} ({member.id})\n"
                          f"**Moderator:** {interaction.user.mention}\n"
                          f"**Warnings Cleared:** {warning_count}",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            await self.bot.log_channel.send(embed=embed)

    @app_commands.command(name="userinfo")
    @app_commands.describe(member="The member to get info about")
    async def userinfo(
        self,
        interaction: discord.Interaction,
        member: Optional[discord.Member] = None
    ):
        """Display information about a user."""
        member = member or interaction.user

        roles = [role.mention for role in reversed(member.roles[1:])]  # Exclude @everyone
        
        embed = discord.Embed(
            title=f"User Information - {member.display_name}",
            color=member.color,
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(
            name="User ID",
            value=member.id,
            inline=True
        )
        embed.add_field(
            name="Account Created",
            value=f"<t:{int(member.created_at.timestamp())}:R>",
            inline=True
        )
        embed.add_field(
            name="Joined Server",
            value=f"<t:{int(member.joined_at.timestamp())}:R>",
            inline=True
        )
        
        if roles:
            embed.add_field(
                name=f"Roles [{len(roles)}]",
                value=" ".join(roles) if len(" ".join(roles)) <= 1024 else f"{len(roles)} roles",
                inline=False
            )
            
        warning_count = len(self.warnings[member.id])
        if warning_count > 0:
            embed.add_field(
                name="Warnings",
                value=warning_count,
                inline=True
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo")
    async def serverinfo(self, interaction: discord.Interaction):
        """Display information about the server."""
        guild = interaction.guild
        
        # Get bot and human member counts
        total_members = guild.member_count
        bot_count = sum(1 for member in guild.members if member.bot)
        human_count = total_members - bot_count
        
        # Get channel counts
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        embed = discord.Embed(
            title=f"Server Information - {guild.name}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
            
        embed.add_field(
            name="Owner",
            value=guild.owner.mention,
            inline=True
        )
        embed.add_field(
            name="Created",
            value=f"<t:{int(guild.created_at.timestamp())}:R>",
            inline=True
        )
        embed.add_field(
            name="Server ID",
            value=guild.id,
            inline=True
        )
        
        embed.add_field(
            name="Members",
            value=f"Total: {total_members}\n"
                  f"Humans: {human_count}\n"
                  f"Bots: {bot_count}",
            inline=True
        )
        
        embed.add_field(
            name="Channels",
            value=f"Text: {text_channels}\n"
                  f"Voice: {voice_channels}\n"
                  f"Categories: {categories}",
            inline=True
        )
        
        embed.add_field(
            name="Roles",
            value=len(guild.roles),
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))
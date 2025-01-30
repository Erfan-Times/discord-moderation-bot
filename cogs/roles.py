import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from datetime import datetime

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addrole")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.describe(
        member="The member to add the role to",
        role="The role to add"
    )
    async def addrole(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        role: discord.Role
    ):
        """Add a role to a member."""
        if role >= interaction.user.top_role and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You cannot add a role that is higher than or equal to your highest role.",
                ephemeral=True
            )
            return

        if role in member.roles:
            await interaction.response.send_message(
                f"{member.mention} already has the {role.mention} role.",
                ephemeral=True
            )
            return

        try:
            await member.add_roles(role, reason=f"Role added by {interaction.user}")
            await interaction.response.send_message(
                f"✅ Added {role.mention} to {member.mention}",
                ephemeral=True
            )

            # Log the action
            if self.bot.log_channel:
                embed = discord.Embed(
                    title="Role Added",
                    description=f"**Member:** {member.mention} ({member.id})\n"
                              f"**Role:** {role.mention}\n"
                              f"**Moderator:** {interaction.user.mention}",
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow()
                )
                await self.bot.log_channel.send(embed=embed)

        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to add that role.",
                ephemeral=True
            )

    @app_commands.command(name="removerole")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.describe(
        member="The member to remove the role from",
        role="The role to remove"
    )
    async def removerole(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        role: discord.Role
    ):
        """Remove a role from a member."""
        if role >= interaction.user.top_role and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You cannot remove a role that is higher than or equal to your highest role.",
                ephemeral=True
            )
            return

        if role not in member.roles:
            await interaction.response.send_message(
                f"{member.mention} doesn't have the {role.mention} role.",
                ephemeral=True
            )
            return

        try:
            await member.remove_roles(role, reason=f"Role removed by {interaction.user}")
            await interaction.response.send_message(
                f"✅ Removed {role.mention} from {member.mention}",
                ephemeral=True
            )

            # Log the action
            if self.bot.log_channel:
                embed = discord.Embed(
                    title="Role Removed",
                    description=f"**Member:** {member.mention} ({member.id})\n"
                              f"**Role:** {role.mention}\n"
                              f"**Moderator:** {interaction.user.mention}",
                    color=discord.Color.red(),
                    timestamp=datetime.utcnow()
                )
                await self.bot.log_channel.send(embed=embed)

        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to remove that role.",
                ephemeral=True
            )

    @app_commands.command(name="createrole")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.describe(
        name="The name of the role",
        color="The color of the role (hex code)",
        hoist="Whether to display the role separately",
        mentionable="Whether the role can be mentioned"
    )
    async def createrole(
        self,
        interaction: discord.Interaction,
        name: str,
        color: Optional[str] = None,
        hoist: Optional[bool] = False,
        mentionable: Optional[bool] = False
    ):
        """Create a new role."""
        try:
            # Convert hex color to discord.Color
            role_color = discord.Color.default()
            if color:
                # Remove # if present
                color = color.strip('#')
                if len(color) == 6:
                    try:
                        role_color = discord.Color(int(color, 16))
                    except ValueError:
                        await interaction.response.send_message(
                            "Invalid color hex code. Please use format: #RRGGBB",
                            ephemeral=True
                        )
                        return

            role = await interaction.guild.create_role(
                name=name,
                color=role_color,
                hoist=hoist,
                mentionable=mentionable,
                reason=f"Role created by {interaction.user}"
            )

            await interaction.response.send_message(
                f"✅ Created role {role.mention}",
                ephemeral=True
            )

            # Log the action
            if self.bot.log_channel:
                embed = discord.Embed(
                    title="Role Created",
                    description=f"**Role:** {role.mention}\n"
                              f"**Name:** {name}\n"
                              f"**Color:** {color if color else 'Default'}\n"
                              f"**Hoisted:** {hoist}\n"
                              f"**Mentionable:** {mentionable}\n"
                              f"**Moderator:** {interaction.user.mention}",
                    color=role_color,
                    timestamp=datetime.utcnow()
                )
                await self.bot.log_channel.send(embed=embed)

        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to create roles.",
                ephemeral=True
            )

    @app_commands.command(name="deleterole")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.describe(role="The role to delete")
    async def deleterole(
        self,
        interaction: discord.Interaction,
        role: discord.Role
    ):
        """Delete a role."""
        if role >= interaction.user.top_role and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You cannot delete a role that is higher than or equal to your highest role.",
                ephemeral=True
            )
            return

        try:
            role_name = role.name
            await role.delete(reason=f"Role deleted by {interaction.user}")
            await interaction.response.send_message(
                f"✅ Deleted role: {role_name}",
                ephemeral=True
            )

            # Log the action
            if self.bot.log_channel:
                embed = discord.Embed(
                    title="Role Deleted",
                    description=f"**Role Name:** {role_name}\n"
                              f"**Role ID:** {role.id}\n"
                              f"**Moderator:** {interaction.user.mention}",
                    color=discord.Color.red(),
                    timestamp=datetime.utcnow()
                )
                await self.bot.log_channel.send(embed=embed)

        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to delete that role.",
                ephemeral=True
            )

    @app_commands.command(name="roleinfo")
    @app_commands.describe(role="The role to get info about")
    async def roleinfo(
        self,
        interaction: discord.Interaction,
        role: discord.Role
    ):
        """Display information about a role."""
        embed = discord.Embed(
            title=f"Role Information - {role.name}",
            color=role.color,
            timestamp=datetime.utcnow()
        )

        # Get member count with this role
        member_count = len(role.members)

        embed.add_field(name="ID", value=role.id, inline=True)
        embed.add_field(name="Color", value=str(role.color), inline=True)
        embed.add_field(name="Member Count", value=member_count, inline=True)
        embed.add_field(name="Mentionable", value=role.mentionable, inline=True)
        embed.add_field(name="Hoisted", value=role.hoist, inline=True)
        embed.add_field(
            name="Created",
            value=f"<t:{int(role.created_at.timestamp())}:R>",
            inline=True
        )
        
        # Show position from bottom (0 is bottom)
        embed.add_field(name="Position", value=role.position, inline=True)
        
        # List key permissions
        perms = []
        for perm, value in role.permissions:
            if value:
                perms.append(perm.replace('_', ' ').title())
        
        if perms:
            embed.add_field(
                name="Key Permissions",
                value='\n'.join(perms[:10]) + (
                    f"\n*and {len(perms)-10} more...*" if len(perms) > 10 else ""
                ),
                inline=False
            )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Roles(bot))
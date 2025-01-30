import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, List

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command_tree = bot.tree

    def get_command_signature(self, command: app_commands.Command) -> str:
        """Get the command signature with parameters."""
        params = []
        for param in command.parameters:
            if param.required:
                params.append(f"<{param.name}>")
            else:
                params.append(f"[{param.name}]")
        
        return f"/{command.name} {' '.join(params)}"

    def get_command_description(self, command: app_commands.Command) -> str:
        """Get the command description and parameter details."""
        desc = [command.description or "No description available."]
        
        if command.parameters:
            desc.append("\nParameters:")
            for param in command.parameters:
                required = "Required" if param.required else "Optional"
                desc.append(f"• {param.name}: {param.description} ({required})")
        
        return "\n".join(desc)

    @app_commands.command(name="help")
    @app_commands.describe(
        command="Specific command to get help for",
        category="Show commands for a specific category"
    )
    async def help(
        self,
        interaction: discord.Interaction,
        command: Optional[str] = None,
        category: Optional[str] = None
    ):
        """Show help for bot commands."""
        if command:
            # Show help for specific command
            cmd = self.command_tree.get_command(command)
            if not cmd:
                await interaction.response.send_message(
                    f"Command '{command}' not found.",
                    ephemeral=True
                )
                return

            embed = discord.Embed(
                title=f"Help - /{command}",
                description=self.get_command_description(cmd),
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Usage",
                value=f"`{self.get_command_signature(cmd)}`"
            )
            
            # Add permission requirements if any
            checks = getattr(cmd, 'checks', [])
            for check in checks:
                if isinstance(check, app_commands.checks.has_permissions):
                    perms = [p.replace('_', ' ').title() for p, v in check.permissions.items() if v]
                    if perms:
                        embed.add_field(
                            name="Required Permissions",
                            value=", ".join(perms),
                            inline=False
                        )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if category:
            # Show commands for specific category
            category = category.lower()
            commands = []
            for cmd in self.command_tree.get_commands():
                cmd_category = cmd.module.split('.')[-1].replace('_', ' ')
                if cmd_category == category:
                    commands.append(cmd)

            if not commands:
                await interaction.response.send_message(
                    f"No commands found in category '{category}'.",
                    ephemeral=True
                )
                return

            embed = discord.Embed(
                title=f"{category.title()} Commands",
                color=discord.Color.blue()
            )

            for cmd in commands:
                embed.add_field(
                    name=self.get_command_signature(cmd),
                    value=cmd.description or "No description available.",
                    inline=False
                )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Show all categories
        categories = {}
        for cmd in self.command_tree.get_commands():
            category = cmd.module.split('.')[-1].replace('_', ' ')
            if category not in categories:
                categories[category] = []
            categories[category].append(cmd)

        embed = discord.Embed(
            title="Bot Help",
            description="Use `/help <command>` for detailed information about a command.\n"
                      "Use `/help category <category>` to see all commands in a category.",
            color=discord.Color.blue()
        )

        for category, commands in categories.items():
            command_list = [f"`/{cmd.name}`" for cmd in commands]
            embed.add_field(
                name=f"{category.title()} Commands",
                value=", ".join(command_list),
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
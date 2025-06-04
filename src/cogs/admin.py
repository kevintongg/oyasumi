import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone
import os
import sys


class Admin(commands.Cog):
    """Admin and owner-only commands"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_autocomplete(self, interaction: discord.Interaction, current: str):
        """Autocomplete function for cog names"""
        # Get all loaded extension names and extract cog names
        cog_names = []
        for extension_name in self.bot.extensions.keys():
            if extension_name.startswith('cogs.'):
                cog_name = extension_name.replace('cogs.', '')
                cog_names.append(cog_name)

        # Filter based on current input
        if current:
            filtered_cogs = [name for name in cog_names if current.lower() in name.lower()]
        else:
            filtered_cogs = cog_names

        # Return as app_commands.Choice objects (max 25)
        return [
            app_commands.Choice(name=name, value=name)
            for name in sorted(filtered_cogs)[:25]
        ]

    @app_commands.command(name='sync', description='Sync slash commands (Owner only)')
    async def sync_commands(self, interaction: discord.Interaction):
        """Manually sync slash commands"""
        owner_id = getattr(self.bot, 'owner_id', None)
        if not owner_id or interaction.user.id != owner_id:
            await interaction.response.send_message('❌ This command is restricted to the bot owner.', ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        try:
            synced = await self.bot.tree.sync()
            await interaction.followup.send(f'✅ Successfully synced {len(synced)} commands', ephemeral=True)
            self.bot.logger.info(f'Manual sync completed by {interaction.user}: {len(synced)} commands')
        except Exception as e:
            await interaction.followup.send(f'❌ Failed to sync commands: {e}', ephemeral=True)
            self.bot.logger.error(f'Manual sync failed: {e}', exc_info=True)

    @app_commands.command(name='reload', description='Reload a specific cog (Owner only)')
    @app_commands.describe(cog='The name of the cog to reload')
    @app_commands.autocomplete(cog=cog_autocomplete)
    async def reload_cog(self, interaction: discord.Interaction, cog: str):
        """Reload a specific cog"""
        owner_id = getattr(self.bot, 'owner_id', None)
        if not owner_id or interaction.user.id != owner_id:
            await interaction.response.send_message('❌ This command is restricted to the bot owner.', ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        try:
            # Try to reload the extension
            await self.bot.reload_extension(f'cogs.{cog}')
            await interaction.followup.send(f'✅ Successfully reloaded `{cog}`', ephemeral=True)
            self.bot.logger.info(f'Cog {cog} reloaded by {interaction.user}')
        except commands.ExtensionNotLoaded:
            await interaction.followup.send(f'❌ Cog `{cog}` is not loaded.', ephemeral=True)
        except commands.ExtensionNotFound:
            await interaction.followup.send(f'❌ Cog `{cog}` not found.', ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f'❌ Failed to reload `{cog}`: {e}', ephemeral=True)
            self.bot.logger.error(f'Failed to reload cog {cog}: {e}', exc_info=True)

    @app_commands.command(name='restart', description='Restart the bot (Owner only)')
    async def restart_bot(self, interaction: discord.Interaction):
        """Restart the bot process"""
        owner_id = getattr(self.bot, 'owner_id', None)
        if not owner_id or interaction.user.id != owner_id:
            await interaction.response.send_message('❌ This command is restricted to the bot owner.', ephemeral=True)
            return

        await interaction.response.send_message('🔄 Restarting bot...', ephemeral=True)
        self.bot.logger.info(f'Bot restart initiated by {interaction.user}')

        # Restart the bot process
        try:
            # Save the current working directory
            original_cwd = os.getcwd()

            # Close the bot connection gracefully
            await self.bot.close()

            # Change to the parent directory where bot.py is located
            if os.path.basename(original_cwd) == 'src':
                os.chdir('..')

            # Restart the process
            os.execv(sys.executable, [sys.executable, 'bot.py'])
        except Exception as e:
            self.bot.logger.error(f'Failed to restart bot: {e}', exc_info=True)

    @app_commands.command(name='shutdown', description='Shutdown the bot (Owner only)')
    async def shutdown(self, interaction: discord.Interaction):
        """Shutdown the bot"""
        owner_id = getattr(self.bot, 'owner_id', None)
        if not owner_id or interaction.user.id != owner_id:
            await interaction.response.send_message('❌ This command is restricted to the bot owner.', ephemeral=True)
            return

        await interaction.response.send_message('👋 Shutting down bot...', ephemeral=True)
        self.bot.logger.info(f'Bot shutdown initiated by {interaction.user}')
        await self.bot.close()


async def setup(bot):
    """Setup function to load the cog"""
    await bot.add_cog(Admin(bot))

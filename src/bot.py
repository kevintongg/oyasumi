import os
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

import discord
from discord import app_commands
from discord.ext import commands

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

load_dotenv()

TOKEN = os.getenv('TOKEN')
OWNER_ID = os.getenv('OWNER_ID')

if not TOKEN:
    raise ValueError('TOKEN must be set in .env file')

if not OWNER_ID:
    raise ValueError('OWNER_ID must be set in .env file')

OWNER_ID = int(OWNER_ID)

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True  # Required for message content access (for non-slash features)
intents.members = True  # Optional: for member-related events


class OyasumiBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',  # Fallback prefix, rarely used with slash commands
            description='Oyasumi - A modern Discord bot for 2025 with slash commands',
            owner_id=OWNER_ID,
            case_insensitive=True,
            intents=intents,
            help_command=None  # We'll use slash commands for help
        )
        self.logger = logging.getLogger('bot')

    async def setup_hook(self):
        """Called when the bot is starting up"""
        self.logger.info('Bot is starting up...')

        # Load extensions first
        await self.load_extensions()

        # Wait a moment for cogs to fully initialize
        await asyncio.sleep(1)

        # Sync slash commands
        try:
            self.logger.info('Syncing slash commands...')
            synced = await self.tree.sync()
            self.logger.info(f'Successfully synced {len(synced)} slash commands')

            # Log the synced commands
            for command in synced:
                self.logger.info(f'Synced command: /{command.name}')

        except Exception as e:
            self.logger.error(f'Failed to sync commands: {e}', exc_info=True)

    async def load_extensions(self):
        """Load all cog files from the cogs directory"""
        # Get the directory where this script is located
        current_dir = Path(__file__).parent
        cogs_dir = current_dir / 'cogs'

        self.logger.info(f'Looking for cogs in: {cogs_dir.absolute()}')

        if not cogs_dir.exists():
            self.logger.error(f'Cogs directory not found: {cogs_dir.absolute()}')
            return

        cog_files = list(cogs_dir.glob('*.py'))
        self.logger.info(f'Found {len(cog_files)} potential cog files')

        for cog_file in cog_files:
            if cog_file.name.startswith('__'):
                continue

            cog_name = f'cogs.{cog_file.stem}'
            try:
                self.logger.info(f'Loading extension: {cog_name}')
                await self.load_extension(cog_name)
                self.logger.info(f'Successfully loaded {cog_name}')
            except Exception as e:
                self.logger.error(f'Failed to load {cog_name}: {e}', exc_info=True)

    async def on_ready(self):
        """Called when bot is fully ready"""
        self.logger.info(f'{self.user} is ready!')
        self.logger.info(f'Bot ID: {self.user.id}')
        self.logger.info(f'Connected to {len(self.guilds)} guild(s)')

        # Log loaded cogs
        self.logger.info(f'Loaded cogs: {[cog for cog in self.cogs.keys()]}')

        # Log available commands
        commands_list = [cmd.name for cmd in self.tree.get_commands()]
        self.logger.info(f'Available slash commands: {commands_list}')

        # Set bot activity
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="for /help | Modern 2025 Bot"
        )
        await self.change_presence(activity=activity)

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Global error handler for slash commands"""
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f'⏰ Command is on cooldown. Try again in {error.retry_after:.2f} seconds.',
                ephemeral=True
            )
            return

        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                '❌ You don\'t have permission to use this command.',
                ephemeral=True
            )
            return

        if isinstance(error, app_commands.BotMissingPermissions):
            await interaction.response.send_message(
                '❌ I don\'t have the required permissions to execute this command.',
                ephemeral=True
            )
            return

        if isinstance(error, app_commands.CommandNotFound):
            self.logger.error(f'Command not found: {error}')
            await interaction.response.send_message(
                '❌ This command is not available. The bot may need to sync its commands.',
                ephemeral=True
            )
            return

        # Log unexpected errors
        self.logger.error(f'Unexpected error in /{interaction.command.name if interaction.command else "unknown"}: {error}', exc_info=error)

        # Send error message
        try:
            if interaction.response.is_done():
                await interaction.followup.send('❌ An unexpected error occurred. The incident has been logged.', ephemeral=True)
            else:
                await interaction.response.send_message('❌ An unexpected error occurred. The incident has been logged.', ephemeral=True)
        except:
            pass


async def main():
    """Main bot runner"""
    bot = OyasumiBot()

    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        logging.info('Received interrupt signal')
    except Exception as e:
        logging.error(f'Bot crashed: {e}', exc_info=e)
    finally:
        if not bot.is_closed():
            await bot.close()


if __name__ == '__main__':
    asyncio.run(main())

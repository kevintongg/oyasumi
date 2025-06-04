from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands


class Help(commands.Cog):
    """Help and information commands"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='help', description='Display help information about bot commands')
    async def help_command(self, interaction: discord.Interaction):
        """Display help information"""
        embed = discord.Embed(
            title="🤖 Oyasumi Bot Help",
            description="Here are all available slash commands:",
            color=discord.Color.blurple(),
            timestamp=datetime.utcnow()
        )

        # Utility Commands
        utility_commands = [
            "`/ping` - Check bot latency and response time",
            "`/botinfo` - Display bot information",
            "`/serverinfo` - Show server information",
            "`/userinfo [@user]` - Display user information",
            "`/avatar [@user]` - Show user's avatar"
        ]
        embed.add_field(name="🔧 Utility Commands", value="\n".join(utility_commands), inline=False)

        # Fun Commands
        fun_commands = [
            "`/hello` - Say hello to the bot",
            "`/coinflip` - Flip a coin",
            "`/roll [sides]` - Roll a dice (default: 6, max: 100)",
            "`/8ball <question>` - Ask the magic 8-ball",
            "`/choose <choices>` - Choose between options (comma-separated)"
        ]
        embed.add_field(name="🎮 Fun Commands", value="\n".join(fun_commands), inline=False)

        # Weather Commands
        weather_commands = [
            "`/weather <location>` - Interactive weather information with forecasts, air quality, and more"
        ]
        embed.add_field(name="🌤️ Weather Commands", value="\n".join(weather_commands), inline=False)

        # Embed Commands
        embed_commands = [
            "`/embed` - Interactive embed creator with buttons",
            "`/quickembed <content>` - Create a quick embed",
            "`/say <message>` - Make the bot say something",
            "`/announce <message>` - Create an announcement (requires manage messages)",
            "`/poll <question> <options...>` - Create a poll with reactions",
            "`/embedinfo [message_id]` - Get embed information"
        ]
        embed.add_field(name="📝 Embed Commands", value="\n".join(embed_commands), inline=False)

        # Add note about interactive features
        embed.add_field(
            name="💡 Interactive Features",
            value="Many commands have interactive buttons and dropdowns for easy use! Try `/weather` or `/embed` to see them in action.",
            inline=False
        )

        embed.set_footer(text=f"Requested by {interaction.user} • Total Commands: {len(self.bot.tree.get_commands())}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    """Setup function to load the cog"""
    await bot.add_cog(Help(bot))

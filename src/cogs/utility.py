import platform
from datetime import datetime, timezone
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os
import aiohttp


class Utility(commands.Cog):
    """Utility commands for bot and server information"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='ping', description='Check the bot\'s latency and response time')
    async def ping(self, interaction: discord.Interaction):
        """Check the bot's latency"""
        import time
        start_time = time.time()
        await interaction.response.send_message("🏓 Pinging...")
        end_time = time.time()

        # Calculate latencies
        api_latency = round(self.bot.latency * 1000, 2)
        response_time = round((end_time - start_time) * 1000, 2)

        embed = discord.Embed(
            title="🏓 Pong!",
            color=discord.Color.green(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="API Latency", value=f"{api_latency}ms", inline=True)
        embed.add_field(name="Response Time", value=f"{response_time}ms", inline=True)
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

        await interaction.edit_original_response(content=None, embed=embed)

    @app_commands.command(name='botinfo', description='Display information about the bot')
    async def botinfo(self, interaction: discord.Interaction):
        """Display information about the bot"""
        embed = discord.Embed(
            title="🤖 Bot Information",
            description="Oyasumi - A modern Discord bot for 2025",
            color=discord.Color.blurple(),
            timestamp=datetime.now(timezone.utc)
        )

        # Bot stats
        embed.add_field(name="📊 Servers", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="👥 Users", value=str(len(self.bot.users)), inline=True)
        embed.add_field(name="⏰ Uptime", value=self.get_uptime(), inline=True)

        # System info
        embed.add_field(name="🐍 Python", value=platform.python_version(), inline=True)
        embed.add_field(name="📚 Discord.py", value=discord.__version__, inline=True)
        embed.add_field(name="🖥️ Platform", value=platform.system(), inline=True)

        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        embed.set_footer(text="Made with ❤️ using Discord.py")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='serverinfo', description='Display information about the current server')
    async def server_info(self, interaction: discord.Interaction):
        """Display information about the current server"""
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
            return

        guild = interaction.guild

        embed = discord.Embed(
            title=f"🏰 {guild.name}",
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )

        # Server stats
        embed.add_field(name="👑 Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="📅 Created", value=guild.created_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="🆔 Server ID", value=guild.id, inline=True)

        embed.add_field(name="👥 Members", value=guild.member_count, inline=True)
        embed.add_field(name="📢 Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="📝 Text Channels", value=len(guild.text_channels), inline=True)

        embed.add_field(name="🔊 Voice Channels", value=len(guild.voice_channels), inline=True)
        embed.add_field(name="👤 Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="😀 Emojis", value=len(guild.emojis), inline=True)

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='userinfo', description='Display information about a user')
    @app_commands.describe(member='The user to get information about (defaults to yourself)')
    async def user_info(self, interaction: discord.Interaction, member: discord.Member = None):
        """Display information about a user"""
        if member is None:
            member = interaction.user

        embed = discord.Embed(
            title=f"👤 {member.display_name}",
            color=member.color if member.color != discord.Color.default() else discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )

        embed.add_field(name="🏷️ Username", value=str(member), inline=True)
        embed.add_field(name="🆔 User ID", value=member.id, inline=True)
        embed.add_field(name="📅 Account Created", value=member.created_at.strftime("%B %d, %Y"), inline=True)

        if interaction.guild and hasattr(member, 'joined_at') and member.joined_at:
            embed.add_field(name="📥 Joined Server", value=member.joined_at.strftime("%B %d, %Y"), inline=True)
            embed.add_field(name="👤 Roles", value=len(member.roles) - 1, inline=True)

        embed.add_field(name="🤖 Bot", value="Yes" if member.bot else "No", inline=True)

        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='avatar', description='Display a user\'s avatar')
    @app_commands.describe(member='The user whose avatar to display (defaults to yourself)')
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        """Display a user's avatar"""
        if member is None:
            member = interaction.user

        embed = discord.Embed(
            title=f"🖼️ {member.display_name}'s Avatar",
            color=member.color if member.color != discord.Color.default() else discord.Color.blue()
        )

        if member.avatar:
            embed.set_image(url=member.avatar.url)
            embed.add_field(name="Download", value=f"[Click here]({member.avatar.url})", inline=False)
        else:
            embed.description = "This user doesn't have a custom avatar."

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='checkowner', description='Check if you are recognized as the bot owner')
    async def check_owner(self, interaction: discord.Interaction):
        """Check if the user is the bot owner"""
        owner_id = getattr(self.bot, 'owner_id', None)
        user_id = interaction.user.id

        embed = discord.Embed(
            title="🔑 Owner Status Check",
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )

        embed.add_field(name="Your Discord ID", value=f"`{user_id}`", inline=False)

        if owner_id:
            embed.add_field(name="Configured Owner ID", value=f"`{owner_id}`", inline=False)

            if user_id == owner_id:
                embed.add_field(
                    name="✅ Owner Status",
                    value="**You are recognized as the bot owner!**\nYou can use owner-only commands like `/sync`, `/reload`, and `/shutdown`.",
                    inline=False
                )
                embed.color = discord.Color.green()
            else:
                embed.add_field(
                    name="❌ Owner Status",
                    value="**You are NOT the bot owner.**\nOwner-only commands will be restricted for you.",
                    inline=False
                )
                embed.color = discord.Color.red()
        else:
            embed.add_field(
                name="⚠️ Configuration Issue",
                value="**No owner ID is configured!**\nCheck your `.env` file and ensure `OWNER_ID` is set.",
                inline=False
            )
            embed.color = discord.Color.orange()

        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='clear', description='Clear a specified number of messages from the chat')
    @app_commands.describe(amount='Number of messages to delete (1-100, default: 10)')
    @app_commands.default_permissions(manage_messages=True)
    async def clear_messages(self, interaction: discord.Interaction, amount: int = 10):
        """Clear messages from the chat"""
        # Check if this is in a guild (servers only)
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in servers!", ephemeral=True)
            return

        # Validate amount
        if amount < 1 or amount > 100:
            await interaction.response.send_message("❌ Amount must be between 1 and 100!", ephemeral=True)
            return

        # Check bot permissions
        if not interaction.guild.me.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ I don't have permission to manage messages in this server!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        try:
            # Get the channel
            channel = interaction.channel

            # Delete messages (this will include the slash command invocation)
            deleted = await channel.purge(limit=amount)

            # Send ephemeral followup to the user
            await interaction.followup.send(f"✅ Successfully cleared {len(deleted)} message(s).", ephemeral=True)

        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to delete messages in this channel!", ephemeral=True)
        except discord.HTTPException as e:
            if "older than 14 days" in str(e):
                await interaction.followup.send("❌ Cannot delete messages older than 14 days. Try a smaller amount.", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ An error occurred while deleting messages: {e}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ An unexpected error occurred: {e}", ephemeral=True)

    @app_commands.command(name='color', description='Display information about a color')
    @app_commands.describe(color='Color in hex (#FF0000), RGB (255,0,0), or name (red)')
    async def color_info(self, interaction: discord.Interaction, color: str):
        """Display information about a color"""
        try:
            # Remove spaces and convert to lowercase
            color = color.replace(' ', '').lower()

            # Color name mapping
            color_names = {
                'red': '#FF0000', 'blue': '#0000FF', 'green': '#008000', 'yellow': '#FFFF00',
                'orange': '#FFA500', 'purple': '#800080', 'pink': '#FFC0CB', 'black': '#000000',
                'white': '#FFFFFF', 'gray': '#808080', 'grey': '#808080', 'brown': '#A52A2A',
                'cyan': '#00FFFF', 'magenta': '#FF00FF', 'lime': '#00FF00', 'navy': '#000080',
                'maroon': '#800000', 'olive': '#808000', 'teal': '#008080', 'silver': '#C0C0C0'
            }

            # Parse the color
            if color in color_names:
                hex_color = color_names[color]
                color_name = color.title()
            elif color.startswith('#'):
                hex_color = color.upper()
                if len(hex_color) != 7:
                    raise ValueError("Invalid hex format")
                color_name = "Custom"
            elif ',' in color:
                # RGB format
                rgb_parts = [int(x.strip()) for x in color.split(',')]
                if len(rgb_parts) != 3 or any(x < 0 or x > 255 for x in rgb_parts):
                    raise ValueError("Invalid RGB format")
                hex_color = f"#{rgb_parts[0]:02X}{rgb_parts[1]:02X}{rgb_parts[2]:02X}"
                color_name = "Custom"
            else:
                raise ValueError("Invalid color format")

            # Convert hex to RGB
            hex_clean = hex_color.lstrip('#')
            rgb = tuple(int(hex_clean[i:i+2], 16) for i in (0, 2, 4))

            # Convert RGB to HSL
            r, g, b = [x/255.0 for x in rgb]
            max_val = max(r, g, b)
            min_val = min(r, g, b)
            diff = max_val - min_val

            # Lightness
            lightness = (max_val + min_val) / 2

            if diff == 0:
                hue = saturation = 0
            else:
                # Saturation
                saturation = diff / (2 - max_val - min_val) if lightness > 0.5 else diff / (max_val + min_val)

                # Hue
                if max_val == r:
                    hue = (60 * ((g - b) / diff) + 360) % 360
                elif max_val == g:
                    hue = (60 * ((b - r) / diff) + 120) % 360
                else:
                    hue = (60 * ((r - g) / diff) + 240) % 360

            # Create color from hex for embed
            embed_color = discord.Color(int(hex_clean, 16))

            embed = discord.Embed(
                title=f"🎨 Color Information",
                color=embed_color,
                timestamp=datetime.now(timezone.utc)
            )

            embed.add_field(name="🏷️ Name", value=color_name, inline=True)
            embed.add_field(name="🔢 Hex", value=hex_color, inline=True)
            embed.add_field(name="🎯 RGB", value=f"{rgb[0]}, {rgb[1]}, {rgb[2]}", inline=True)
            embed.add_field(name="🌈 HSL", value=f"{hue:.0f}°, {saturation*100:.0f}%, {lightness*100:.0f}%", inline=True)

            # Add brightness info
            brightness = (rgb[0] * 0.299 + rgb[1] * 0.587 + rgb[2] * 0.114) / 255
            brightness_text = "Bright" if brightness > 0.5 else "Dark"
            embed.add_field(name="💡 Brightness", value=f"{brightness*100:.1f}% ({brightness_text})", inline=True)

            # Add complementary color
            comp_rgb = (255 - rgb[0], 255 - rgb[1], 255 - rgb[2])
            comp_hex = f"#{comp_rgb[0]:02X}{comp_rgb[1]:02X}{comp_rgb[2]:02X}"
            embed.add_field(name="🔄 Complementary", value=comp_hex, inline=True)

            embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

            await interaction.response.send_message(embed=embed)

        except ValueError as e:
            await interaction.response.send_message(
                "❌ Invalid color format! Use:\n"
                "• **Hex:** `#FF0000` or `#f00`\n"
                "• **RGB:** `255,0,0`\n"
                "• **Name:** `red`, `blue`, `green`, etc.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Error processing color: {e}", ephemeral=True)

    @app_commands.command(name='timer', description='Start a countdown timer')
    @app_commands.describe(duration='Duration in seconds, or format like "5m", "1h30m", "90s"')
    async def timer(self, interaction: discord.Interaction, duration: str):
        """Start a countdown timer"""
        try:
            # Parse duration
            total_seconds = self.parse_duration(duration)

            if total_seconds <= 0:
                await interaction.response.send_message("❌ Duration must be greater than 0!", ephemeral=True)
                return

            if total_seconds > 86400:  # 24 hours max
                await interaction.response.send_message("❌ Maximum timer duration is 24 hours!", ephemeral=True)
                return

            # Format duration for display
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            duration_str = []
            if hours > 0:
                duration_str.append(f"{hours}h")
            if minutes > 0:
                duration_str.append(f"{minutes}m")
            if seconds > 0 or not duration_str:
                duration_str.append(f"{seconds}s")

            duration_display = " ".join(duration_str)

            embed = discord.Embed(
                title="⏱️ Timer Started",
                description=f"Timer set for **{duration_display}**\nYou will be notified when it's done!",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_footer(text=f"Started by {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

            await interaction.response.send_message(embed=embed)

            # Start the timer
            await asyncio.sleep(total_seconds)

            # Timer finished
            finish_embed = discord.Embed(
                title="⏰ Timer Finished!",
                description=f"Your **{duration_display}** timer is complete!",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc)
            )

            await interaction.followup.send(f"{interaction.user.mention}", embed=finish_embed)

        except ValueError as e:
            await interaction.response.send_message(
                "❌ Invalid duration format! Examples:\n"
                "• `30` (30 seconds)\n"
                "• `5m` (5 minutes)\n"
                "• `1h30m` (1 hour 30 minutes)\n"
                "• `90s` (90 seconds)",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Error starting timer: {e}", ephemeral=True)

    def parse_duration(self, duration_str: str) -> int:
        """Parse duration string into seconds"""
        duration_str = duration_str.lower().strip()

        # If it's just a number, treat as seconds
        if duration_str.isdigit():
            return int(duration_str)

        total_seconds = 0
        current_number = ""

        for char in duration_str:
            if char.isdigit():
                current_number += char
            elif char in 'hms':
                if current_number:
                    num = int(current_number)
                    if char == 'h':
                        total_seconds += num * 3600
                    elif char == 'm':
                        total_seconds += num * 60
                    elif char == 's':
                        total_seconds += num
                    current_number = ""

        # Handle trailing number without unit (treat as seconds)
        if current_number:
            total_seconds += int(current_number)

        return total_seconds

    def get_uptime(self):
        """Calculate bot uptime"""
        return "Since last restart"


async def setup(bot):
    """Setup function to load the cog"""
    await bot.add_cog(Utility(bot))

import discord
import random
import asyncio
from discord import app_commands
from discord.ext import commands


class EmbedView(discord.ui.View):
    """Interactive view for embed creator"""

    def __init__(self, bot):
        super().__init__(timeout=300)  # 5 minute timeout
        self.bot = bot
        self.embed_data = {
            'title': None,
            'description': None,
            'color': discord.Color.blue(),
            'author': None,
            'footer': None,
            'image': None,
            'thumbnail': None,
            'fields': []
        }

    @discord.ui.button(label='Set Title', style=discord.ButtonStyle.primary, emoji='📝')
    async def set_title(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Set the embed title"""
        modal = EmbedModal('title', 'Set Title', 'Enter the embed title:', self.embed_data['title'])
        modal.embed_view = self
        await interaction.response.send_modal(modal)

    @discord.ui.button(label='Set Description', style=discord.ButtonStyle.primary, emoji='📄')
    async def set_description(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Set the embed description"""
        modal = EmbedModal('description', 'Set Description', 'Enter the embed description:', self.embed_data['description'])
        modal.embed_view = self
        await interaction.response.send_modal(modal)

    @discord.ui.button(label='Set Color', style=discord.ButtonStyle.secondary, emoji='🎨')
    async def set_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Set the embed color"""
        view = ColorSelectView(self)
        await interaction.response.send_message("Choose a color for your embed:", view=view, ephemeral=True)

    @discord.ui.button(label='Add Field', style=discord.ButtonStyle.success, emoji='➕')
    async def add_field(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Add a field to the embed"""
        modal = FieldModal(self.embed_data)
        modal.embed_view = self
        await interaction.response.send_modal(modal)

    @discord.ui.button(label='Send Embed', style=discord.ButtonStyle.success, emoji='🚀', row=1)
    async def send_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Send the created embed"""
        embed = self.create_embed()
        await interaction.response.send_message("Here's your embed:", embed=embed)

    @discord.ui.button(label='Preview', style=discord.ButtonStyle.secondary, emoji='👀', row=1)
    async def preview_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Preview the embed"""
        embed = self.create_embed()
        updated_view = self.create_updated_view()
        await interaction.response.edit_message(embed=embed, view=updated_view)

    def create_embed(self):
        """Create the Discord embed from stored data"""
        embed = discord.Embed(
            title=self.embed_data['title'],
            description=self.embed_data['description'],
            color=self.embed_data['color']
        )

        if self.embed_data['author']:
            embed.set_author(name=self.embed_data['author'])

        if self.embed_data['footer']:
            embed.set_footer(text=self.embed_data['footer'])

        if self.embed_data['image']:
            embed.set_image(url=self.embed_data['image'])

        if self.embed_data['thumbnail']:
            embed.set_thumbnail(url=self.embed_data['thumbnail'])

        for field in self.embed_data['fields']:
            embed.add_field(name=field['name'], value=field['value'], inline=field.get('inline', True))

        return embed

    def create_updated_view(self):
        """Create updated view showing current data"""
        embed = discord.Embed(
            title="🛠️ Embed Creator",
            description="Use the buttons below to create your custom embed!",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="📝 Title",
            value=self.embed_data['title'] or "Not set",
            inline=True
        )
        embed.add_field(
            name="📄 Description",
            value=(self.embed_data['description'][:50] + "...") if self.embed_data['description'] and len(self.embed_data['description']) > 50 else (self.embed_data['description'] or "Not set"),
            inline=True
        )
        embed.add_field(
            name="🎨 Color",
            value=str(self.embed_data['color']),
            inline=True
        )
        embed.add_field(
            name="📋 Fields",
            value=f"{len(self.embed_data['fields'])} field(s)",
            inline=True
        )

        return embed


class EmbedModal(discord.ui.Modal):
    """Modal for setting embed properties"""

    def __init__(self, field_type, title, label, current_value=None):
        super().__init__(title=title)
        self.field_type = field_type
        self.embed_view = None

        if field_type == 'title':
            max_length = 256
        else:  # description
            max_length = 4000

        self.input = discord.ui.TextInput(
            label=label,
            default=current_value,
            max_length=max_length,
            style=discord.TextStyle.long if field_type == 'description' else discord.TextStyle.short,
            required=False
        )
        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        self.embed_view.embed_data[self.field_type] = self.input.value if self.input.value else None
        updated_embed = self.embed_view.create_updated_view()
        await interaction.response.edit_message(embed=updated_embed, view=self.embed_view)


class FieldModal(discord.ui.Modal):
    """Modal for adding fields"""

    def __init__(self, embed_data):
        super().__init__(title="Add Field")
        self.embed_data = embed_data
        self.embed_view = None

        self.name_input = discord.ui.TextInput(
            label="Field Name",
            max_length=256,
            placeholder="Enter field name..."
        )

        self.value_input = discord.ui.TextInput(
            label="Field Value",
            style=discord.TextStyle.long,
            max_length=1024,
            placeholder="Enter field content..."
        )

        self.add_item(self.name_input)
        self.add_item(self.value_input)

    async def on_submit(self, interaction: discord.Interaction):
        self.embed_data['fields'].append({
            'name': self.name_input.value,
            'value': self.value_input.value,
            'inline': True
        })

        updated_embed = self.embed_view.create_updated_view()
        await interaction.response.edit_message(embed=updated_embed, view=self.embed_view)


class ColorSelectView(discord.ui.View):
    """View for selecting embed colors"""

    def __init__(self, embed_view):
        super().__init__(timeout=60)
        self.embed_view = embed_view

    @discord.ui.select(
        placeholder="Choose a color...",
        options=[
            discord.SelectOption(label="Blue", emoji="🔵", value="blue"),
            discord.SelectOption(label="Red", emoji="🔴", value="red"),
            discord.SelectOption(label="Green", emoji="🟢", value="green"),
            discord.SelectOption(label="Yellow", emoji="🟡", value="yellow"),
            discord.SelectOption(label="Purple", emoji="🟣", value="purple"),
            discord.SelectOption(label="Orange", emoji="🟠", value="orange"),
            discord.SelectOption(label="Gold", emoji="🟨", value="gold"),
            discord.SelectOption(label="Random", emoji="🎲", value="random"),
        ]
    )
    async def color_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        color_map = {
            'blue': discord.Color.blue(),
            'red': discord.Color.red(),
            'green': discord.Color.green(),
            'yellow': discord.Color.yellow(),
            'purple': discord.Color.purple(),
            'orange': discord.Color.orange(),
            'gold': discord.Color.gold(),
            'random': self.get_random_color()
        }

        self.embed_view.embed_data['color'] = color_map[select.values[0]]
        updated_embed = self.embed_view.create_updated_view()

        # Update the original message
        try:
            await interaction.response.edit_message(content="Color updated!", view=None)
            # We need to edit the original embed message, but we can't do it directly here
            # The embed view will be updated when the user interacts with it next
        except:
            await interaction.response.send_message("Color updated!", ephemeral=True)

    def get_random_color(self):
        """Get a random color"""
        colors = [
            discord.Color.red(),
            discord.Color.blue(),
            discord.Color.green(),
            discord.Color.yellow(),
            discord.Color.purple(),
            discord.Color.orange(),
            discord.Color.magenta(),
            discord.Color.gold(),
            discord.Color.blurple(),
            discord.Color.dark_blue(),
            discord.Color.dark_green(),
        ]
        return random.choice(colors)


class Embed(commands.Cog):
    """Commands for creating and managing embeds"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='embed', description='Interactive embed creator with buttons')
    async def create_embed(self, interaction: discord.Interaction):
        """Interactive embed creator"""
        view = EmbedView(self.bot)
        embed = discord.Embed(
            title="🛠️ Embed Creator",
            description="Use the buttons below to create your custom embed!",
            color=discord.Color.blue()
        )
        embed.add_field(name="📝 Title", value="Not set", inline=True)
        embed.add_field(name="📄 Description", value="Not set", inline=True)
        embed.add_field(name="🎨 Color", value="Blue", inline=True)

        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name='quickembed', description='Create a quick embed with just a description')
    @app_commands.describe(content='The content for your embed')
    async def quick_embed(self, interaction: discord.Interaction, content: str):
        """Create a quick embed with just a description"""
        embed = discord.Embed(
            description=content,
            color=self.get_random_color(),
            timestamp=interaction.created_at
        )

        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.avatar.url if interaction.user.avatar else None
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='say', description='Make the bot say something in an embed')
    @app_commands.describe(message='The message to say')
    async def say_embed(self, interaction: discord.Interaction, message: str):
        """Make the bot say something in an embed"""
        embed = discord.Embed(
            description=message,
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='announce', description='Create an announcement embed')
    @app_commands.describe(announcement='The announcement message')
    @app_commands.default_permissions(manage_messages=True)
    async def announce(self, interaction: discord.Interaction, announcement: str):
        """Create an announcement embed (requires manage messages permission)"""
        embed = discord.Embed(
            title="📢 Announcement",
            description=announcement,
            color=discord.Color.gold(),
            timestamp=interaction.created_at
        )

        embed.set_author(
            name=interaction.guild.name if interaction.guild else "Announcement",
            icon_url=interaction.guild.icon.url if interaction.guild and interaction.guild.icon else None
        )

        embed.set_footer(text=f"Announced by {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

        await interaction.response.send_message("@everyone", embed=embed)

    @app_commands.command(name='poll', description='Create a poll with reactions')
    @app_commands.describe(
        question='The poll question',
        option1='First option',
        option2='Second option',
        option3='Third option (optional)',
        option4='Fourth option (optional)',
        option5='Fifth option (optional)'
    )
    async def poll(self, interaction: discord.Interaction, question: str, option1: str, option2: str,
                  option3: str = None, option4: str = None, option5: str = None):
        """Create a poll with reactions"""
        options = [option1, option2]
        if option3:
            options.append(option3)
        if option4:
            options.append(option4)
        if option5:
            options.append(option5)

        # Number emojis for options
        number_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']

        embed = discord.Embed(
            title="📊 Poll",
            description=f"**{question}**",
            color=discord.Color.blue(),
            timestamp=interaction.created_at
        )

        # Add options to embed
        options_text = ""
        for i, option in enumerate(options):
            options_text += f"{number_emojis[i]} {option}\n"

        embed.add_field(name="Options", value=options_text, inline=False)
        embed.set_footer(text=f"Poll created by {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

        # Send poll and add reactions
        await interaction.response.send_message(embed=embed)
        poll_message = await interaction.original_response()

        for i in range(len(options)):
            await poll_message.add_reaction(number_emojis[i])

    @app_commands.command(name='embedinfo', description='Get information about an embed')
    @app_commands.describe(message_id='The ID of the message containing the embed (optional)')
    async def embed_info(self, interaction: discord.Interaction, message_id: str = None):
        """Get information about an embed in the current channel"""
        if message_id:
            try:
                message = await interaction.channel.fetch_message(int(message_id))
            except (discord.NotFound, ValueError):
                await interaction.response.send_message("❌ Message not found!", ephemeral=True)
                return
        else:
            # Get the last message with an embed in the channel
            async for msg in interaction.channel.history(limit=50):
                if msg.embeds and msg.id != interaction.id:
                    message = msg
                    break
            else:
                await interaction.response.send_message("❌ No embeds found in recent messages!", ephemeral=True)
                return

        if not message.embeds:
            await interaction.response.send_message("❌ That message doesn't contain an embed!", ephemeral=True)
        return

        embed_to_analyze = message.embeds[0]

        # Create info embed
        info_embed = discord.Embed(
            title="📋 Embed Information",
            color=discord.Color.green()
        )

        info_embed.add_field(name="Title", value=embed_to_analyze.title or "None", inline=False)
        info_embed.add_field(name="Description", value=embed_to_analyze.description[:100] + "..." if embed_to_analyze.description and len(embed_to_analyze.description) > 100 else embed_to_analyze.description or "None", inline=False)
        info_embed.add_field(name="Color", value=str(embed_to_analyze.color), inline=True)
        info_embed.add_field(name="Fields", value=len(embed_to_analyze.fields), inline=True)
        info_embed.add_field(name="Message ID", value=message.id, inline=True)

        if embed_to_analyze.author:
            info_embed.add_field(name="Author", value=embed_to_analyze.author.name, inline=True)
        if embed_to_analyze.footer:
            info_embed.add_field(name="Footer", value=embed_to_analyze.footer.text, inline=True)

        await interaction.response.send_message(embed=info_embed)

    def get_random_color(self):
        """Get a random color"""
        colors = [
            discord.Color.red(),
            discord.Color.blue(),
            discord.Color.green(),
            discord.Color.yellow(),
            discord.Color.purple(),
            discord.Color.orange(),
            discord.Color.magenta(),
            discord.Color.gold(),
            discord.Color.blurple(),
            discord.Color.dark_blue(),
            discord.Color.dark_green(),
        ]
        return random.choice(colors)


async def setup(bot):
    """Setup function to load the cog"""
    await bot.add_cog(Embed(bot))

# Oyasumi Discord Bot 🌙

A modern Discord bot built with Discord.py 2.5.2 for 2025, featuring **slash commands**, interactive UI components, comprehensive error handling, and a beautiful user interface.

## ✨ Features

- **Modern Slash Commands**: Uses Discord's native slash command system with autocomplete and validation
- **Interactive UI**: Beautiful buttons, modals, and interactive embed creation
- **Modern Architecture**: Built with Discord.py 2.5.2 using the latest async/await patterns
- **Comprehensive Commands**: Utility commands, embed creation, polls, and more
- **Clean UI**: Beautiful embeds with emojis and consistent styling
- **Error Handling**: Robust error handling with user-friendly messages
- **Modular Design**: Organized cog system for easy maintenance and expansion
- **Secure Configuration**: Environment variable-based configuration
- **Logging**: Comprehensive logging for debugging and monitoring

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- A Discord bot application ([Create one here](https://discord.com/developers/applications))

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd oyasumi
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env with your bot's information
   # You need:
   # - TOKEN: Your bot's token from Discord Developer Portal
   # - OWNER_ID: Your Discord user ID
   ```

4. **Run the bot**
   ```bash
   python run.py
   # OR
   python src/bot.py
   ```

5. **Invite the bot to your server**
   - Go to the Discord Developer Portal
   - Select your application → OAuth2 → URL Generator
   - Select "bot" and "applications.commands" scopes
   - Choose necessary permissions
   - Use the generated URL to invite your bot

## 🎯 Slash Commands

All commands use Discord's modern slash command system. Simply type `/` in any text channel to see available commands!

### Basic Commands
- `/hello` - Greet the bot
- `/ping` - Check bot latency and response time
- `/botinfo` - Display bot information
- `/serverinfo` - Show server information
- `/userinfo [@user]` - Display user information
- `/avatar [@user]` - Show user's avatar

### Fun Commands
- `/coinflip` - Flip a coin
- `/roll [sides]` - Roll a dice (default: 6 sides, max: 100)
- `/8ball <question>` - Ask the magic 8-ball
- `/choose <choices>` - Choose between options (comma-separated)

### Embed Commands
- `/embed` - **Interactive embed creator with buttons and modals**
- `/quickembed <message>` - Create a quick embed
- `/say <message>` - Make the bot say something in an embed
- `/announce <message>` - Create an announcement (requires manage messages)
- `/poll <question> <option1> <option2> [option3] [option4] [option5]` - Create a poll with reactions
- `/embedinfo [message_id]` - Get information about an embed
- `/help` - Display help information about bot commands

### Owner Commands (Bot owner only)
- `/reload <cog>` - Reload a specific cog
- `/sync` - Manually sync slash commands
- `/shutdown` - Safely shutdown the bot

## 🛠️ Configuration

The bot uses environment variables for configuration. Create a `.env` file in the root directory:

```env
# Discord Bot Configuration
TOKEN=your_bot_token_here
OWNER_ID=your_discord_user_id_here
```

### Getting Your Bot Token
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application or select an existing one
3. Go to the "Bot" section
4. Copy the token (keep this secret!)

### Getting Your User ID
1. Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
2. Right-click on your username and select "Copy ID"

### Bot Permissions
Your bot needs these permissions:
- **Send Messages** - To send responses
- **Use Slash Commands** - To register and use slash commands
- **Embed Links** - To send rich embeds
- **Add Reactions** - For poll functionality
- **Read Message History** - For embed info command

## 📁 Project Structure

```
oyasumi/
├── src/
│   ├── bot.py              # Main bot file with slash command setup
│   └── cogs/               # Bot commands organized in cogs
│       ├── basic.py        # Basic utility slash commands
│       └── embed.py        # Embed-related slash commands with UI
├── requirements.txt        # Python dependencies
├── env.example            # Environment variables template
├── run.py                 # Convenient startup script
├── README.md              # This file
└── .gitignore            # Git ignore file
```

## 🔧 Development

### Adding New Slash Commands

Create commands using the `@app_commands.command` decorator:

```python
@app_commands.command(name='example', description='An example slash command')
@app_commands.describe(argument='Description of the argument')
async def example_command(self, interaction: discord.Interaction, argument: str):
    """An example slash command"""
    embed = discord.Embed(
        title="Example",
        description=f"You provided: {argument}",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)
```

### Creating Interactive UI Components

The bot supports Discord's modern UI components:

```python
class MyView(discord.ui.View):
    @discord.ui.button(label='Click Me!', style=discord.ButtonStyle.primary)
    async def my_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Button clicked!", ephemeral=True)

# Send with the view
await interaction.response.send_message("Click the button:", view=MyView())
```

### Creating New Cogs

```python
import discord
from discord import app_commands
from discord.ext import commands

class MyCog(commands.Cog):
    """Description of your cog"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name='mycommand', description='My command description')
    async def my_command(self, interaction: discord.Interaction):
        """My slash command"""
        await interaction.response.send_message("Hello from my cog!")

async def setup(bot):
    await bot.add_cog(MyCog(bot))
```

## 📝 What's New in 2025 Update

- **🔥 Slash Commands**: Complete conversion to Discord's modern slash command system
- **🎨 Interactive UI**: Buttons, modals, and views for better user experience
- **⚡ Discord.py 2.5.2**: Latest version with all modern features
- **🏗️ Improved Architecture**: Class-based bot with proper inheritance
- **🛡️ Better Error Handling**: Comprehensive error handling with user-friendly messages
- **📊 Modern Logging**: File and console logging with proper formatting
- **🔒 Security**: Environment variable configuration instead of hardcoded tokens
- **🎯 UI/UX**: Beautiful embeds with emojis and consistent styling
- **🧹 Code Quality**: Clean, documented, and maintainable code
- **⚙️ Auto-sync**: Automatic command synchronization on startup

## 🚀 Modern Features

### Slash Command Benefits
- ✅ **Autocomplete**: Discord shows available commands as you type
- ✅ **Parameter Validation**: Automatic type checking and validation
- ✅ **Better Discovery**: Users can easily find commands with `/`
- ✅ **Mobile Friendly**: Better experience on mobile devices
- ✅ **Rich Descriptions**: Commands show helpful descriptions and parameter info

### Interactive Components
- 🔘 **Buttons**: Interactive buttons for actions
- 📝 **Modals**: Pop-up forms for user input
- 📋 **Select Menus**: Dropdown menus for choices
- ⏱️ **Timeouts**: Automatic cleanup of expired interactions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you need help with the bot:

1. Check the [Discord.py documentation](https://discordpy.readthedocs.io/)
2. Review the error logs in `bot.log`
3. Make sure your `.env` file is properly configured
4. Ensure the bot has the necessary permissions in your Discord server
5. Make sure to invite the bot with both "bot" and "applications.commands" scopes

## 🔗 Useful Links

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Discord Developer Portal](https://discord.com/developers/applications)
- [Discord Bot Permissions Calculator](https://discordapi.com/permissions.html)
- [Discord.py Slash Commands Guide](https://discordpy.readthedocs.io/en/stable/interactions/api.html)

## 🎯 Command Examples

### Interactive Embed Creator
```
/embed
```
Creates an interactive embed creator with buttons for setting title, description, and color.

### Quick Poll
```
/poll question:"What's your favorite color?" option1:"Red" option2:"Blue" option3:"Green"
```
Creates a poll with reaction voting.

### Magic 8-Ball
```
/8ball question:"Will it rain tomorrow?"
```
Ask the magic 8-ball any yes/no question.

---

Made with ❤️ using Discord.py 2.5.2 and modern slash commands

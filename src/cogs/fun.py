import random
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone


class Fun(commands.Cog):
    """Fun and entertainment commands"""

    def __init__(self, bot):
        self.bot = bot

        # Inspirational quotes collection
        self.quotes = [
            ("The only way to do great work is to love what you do.", "Steve Jobs"),
            ("Innovation distinguishes between a leader and a follower.", "Steve Jobs"),
            ("Life is what happens to you while you're busy making other plans.", "John Lennon"),
            ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
            ("It is during our darkest moments that we must focus to see the light.", "Aristotle"),
            ("The way to get started is to quit talking and begin doing.", "Walt Disney"),
            ("Don't let yesterday take up too much of today.", "Will Rogers"),
            ("You learn more from failure than from success. Don't let it stop you. Failure builds character.", "Unknown"),
            ("If you are working on something that you really care about, you don't have to be pushed. The vision pulls you.", "Steve Jobs"),
            ("Experience is a hard teacher because she gives the test first, the lesson afterwards.", "Vernon Law"),
            ("To live is the rarest thing in the world. Most people just exist.", "Oscar Wilde"),
            ("Success is not final, failure is not fatal: it is the courage to continue that counts.", "Winston Churchill"),
            ("The only impossible journey is the one you never begin.", "Tony Robbins"),
            ("In the middle of difficulty lies opportunity.", "Albert Einstein"),
            ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
            ("The only person you are destined to become is the person you decide to be.", "Ralph Waldo Emerson"),
            ("Go confidently in the direction of your dreams. Live the life you have imagined.", "Henry David Thoreau"),
            ("When you reach the end of your rope, tie a knot in it and hang on.", "Franklin D. Roosevelt"),
            ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson"),
            ("Keep your face always toward the sunshine—and shadows will fall behind you.", "Walt Whitman"),
            ("Whether you think you can or you think you can't, you're right.", "Henry Ford"),
            ("The best time to plant a tree was 20 years ago. The second best time is now.", "Chinese Proverb"),
            ("Your limitation—it's only your imagination.", "Unknown"),
            ("Great things never come from comfort zones.", "Unknown"),
            ("Dream it. Wish it. Do it.", "Unknown"),
            ("Success doesn't just find you. You have to go out and get it.", "Unknown"),
            ("The harder you work for something, the greater you'll feel when you achieve it.", "Unknown"),
            ("Dream bigger. Do bigger.", "Unknown"),
            ("Don't stop when you're tired. Stop when you're done.", "Unknown"),
            ("Wake up with determination. Go to bed with satisfaction.", "Unknown"),
            ("Do something today that your future self will thank you for.", "Sean Patrick Flanery"),
            ("Little things make big days.", "Unknown"),
            ("It's going to be hard, but hard does not mean impossible.", "Unknown"),
            ("Don't wait for opportunity. Create it.", "Unknown"),
            ("Sometimes we're tested not to show our weaknesses, but to discover our strengths.", "Unknown"),
            ("The key to success is to focus on goals, not obstacles.", "Unknown"),
            ("Dream it. Believe it. Build it.", "Unknown")
        ]

    @app_commands.command(name='hello', description='Say hello to the bot')
    async def hello(self, interaction: discord.Interaction):
        """Say hello to the bot"""
        greetings = [
            f"Hello {interaction.user.mention}! 👋",
            f"Hi there {interaction.user.display_name}! 😊",
            f"Hey {interaction.user.mention}! How are you doing? 🌟",
            f"Greetings {interaction.user.display_name}! ✨"
        ]
        await interaction.response.send_message(random.choice(greetings))

    @app_commands.command(name='coinflip', description='Flip a coin')
    async def coin_flip(self, interaction: discord.Interaction):
        """Flip a coin"""
        result = random.choice(['Heads', 'Tails'])
        emoji = "🪙" if result == "Heads" else "🏮"

        embed = discord.Embed(
            title="🪙 Coin Flip",
            description=f"{emoji} **{result}!**",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='roll', description='Roll a dice with specified number of sides')
    @app_commands.describe(sides='Number of sides on the dice (default: 6, max: 100)')
    async def roll_dice(self, interaction: discord.Interaction, sides: int = 6):
        """Roll a dice with specified number of sides (default: 6)"""
        if sides < 2:
            await interaction.response.send_message("❌ Dice must have at least 2 sides!", ephemeral=True)
            return
        if sides > 100:
            await interaction.response.send_message("❌ Dice cannot have more than 100 sides!", ephemeral=True)
            return

        result = random.randint(1, sides)
        embed = discord.Embed(
            title="🎲 Dice Roll",
            description=f"🎯 **{result}** (out of {sides})",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='8ball', description='Ask the magic 8-ball a question')
    @app_commands.describe(question='The question you want to ask the magic 8-ball')
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        """Ask the magic 8-ball a question"""
        responses = [
            "🔮 It is certain",
            "🔮 It is decidedly so",
            "🔮 Without a doubt",
            "🔮 Yes definitely",
            "🔮 You may rely on it",
            "🔮 As I see it, yes",
            "🔮 Most likely",
            "🔮 Outlook good",
            "🔮 Yes",
            "🔮 Signs point to yes",
            "🔮 Reply hazy, try again",
            "🔮 Ask again later",
            "🔮 Better not tell you now",
            "🔮 Cannot predict now",
            "🔮 Concentrate and ask again",
            "🔮 Don't count on it",
            "🔮 My reply is no",
            "🔮 My sources say no",
            "🔮 Outlook not so good",
            "🔮 Very doubtful"
        ]

        embed = discord.Embed(
            title="🎱 Magic 8-Ball",
            color=discord.Color.purple()
        )
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=random.choice(responses), inline=False)
        embed.set_footer(text=f"Asked by {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='choose', description='Choose between multiple options')
    @app_commands.describe(
        choice1='First option',
        choice2='Second option',
        choice3='Third option (optional)',
        choice4='Fourth option (optional)',
        choice5='Fifth option (optional)',
        choice6='Sixth option (optional)'
    )
    async def choose(self, interaction: discord.Interaction,
                    choice1: str, choice2: str, choice3: str = None,
                    choice4: str = None, choice5: str = None, choice6: str = None):
        """Choose between multiple options"""
        # Collect all non-None choices
        options = [choice1, choice2]
        for choice in [choice3, choice4, choice5, choice6]:
            if choice:
                options.append(choice)

        chosen = random.choice(options)
        embed = discord.Embed(
            title="🤔 Decision Maker",
            description=f"🎯 I choose: **{chosen}**",
            color=discord.Color.orange()
        )
        embed.add_field(name="Options", value=", ".join(options), inline=False)
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='quote', description='Get an inspirational quote')
    async def inspirational_quote(self, interaction: discord.Interaction):
        """Get a random inspirational quote"""
        quote_text, author = random.choice(self.quotes)

        embed = discord.Embed(
            title="✨ Inspirational Quote",
            description=f'*"{quote_text}"*',
            color=discord.Color.gold(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="Author", value=f"— {author}", inline=False)
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    """Setup function to load the cog"""
    await bot.add_cog(Fun(bot))

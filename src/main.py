from config.settings import token
from discord.ext import commands
import discord


def get_prefix(client, message):
    prefixes = ['.']

    return commands.when_mentioned_or(*prefixes)(client, message)


bot = commands.Bot(
    command_prefix=get_prefix,
    description='A Discord bot written in Python using Discord.py',
    owner_id=91677911823704064,
    case_insensitive=True
)

cogs = [
    'cogs.basic',
    'cogs.embed'
]


@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user} – {bot.user.id}\nVersion: {discord.__version__}')
    bot.remove_command('help')
    for cog in cogs:
        bot.load_extension(cog)
    return


# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return
#     if message.content.startswith('hello'):
#         embed = discord.Embed()
#         embed.add_field(name='Message', value="hi!", inline=False)
#         await message.channel.send(embed=embed)


bot.run(token, bot=True)

# from discord.ext import commands
# from dotenv import load_dotenv
# import os
#
# load_dotenv()
#
#
# def get_prefix(client, message):
#     prefixes = ['.']  # sets the prefixes, u can keep it as an array of only 1 item if you need only one prefix
#
#     if not message.guild:
#         prefixes = ['==']  # Only allow '==' as a prefix when in DMs
#
#     # Allow users to @mention the bot instead of using a prefix when using a command.
#     return commands.when_mentioned_or(*prefixes)(client, message)
#
#
# bot = commands.Bot(
#     # Create a new bot
#     command_prefix=get_prefix,  # Set the prefix
#     description='A bot used for tutorial',  # Set a description for the bot
#     owner_id=91677911823704064,  # Your unique User ID
#     case_insensitive=True  # Make the commands case insensitive
# )
#
# # case_insensitive=True is used as the commands are case sensitive by default
#
# cogs = ['cogs.basic', 'cogs.embed']
#
#
# @bot.event
# async def on_ready():
#     print(f'Logged in as {bot.user.name} - {bot.user.id}')
#     bot.remove_command('help')
#     # Removes the help command
#     # Make sure to do this before loading the cogs
#     for cog in cogs:
#         bot.load_extension(cog)
#     return
#
#
# # Finally, login the bot
# bot.run(os.environ.get('TOKEN'), bot=True, reconnect=True)

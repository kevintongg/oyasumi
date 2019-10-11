from datetime import datetime as dt
from discord.ext import commands
from misc.stuff import jp_en_words
import random
import http.client
import json
import urllib.parse

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='ping',
        description='Pings a message',
        aliases=['p']
    )
    async def ping(self, ctx):
        start = dt.timestamp(dt.now())

        message = await ctx.send(content='Pinging!')
        await message.edit(content=f'Pong!\nMessage took {(dt.timestamp(dt.now()) - start) * 1000}ms.')

    @commands.command(
        name='jpfun',
        description='Fun with Japanese!'
    )
    async def jp_fun(self, ctx):
        message = random.choice(jp_en_words)
        await ctx.send(content=message)

    @commands.command(
        name='coinflip',
        description='Flips a coin'
    )
    async def coin_flip(self, ctx):
        coin_sides = [
            'Heads!',
            'Tails!'
        ]
        message = random.choice(coin_sides)

        await ctx.send(content=message)

    @commands.command(name='8ball')
    async def eight_ball(self, ctx, question: str):
        conn = http.client.HTTPSConnection('8ball.delegator.com')
        question = urllib.parse.quote(question)
        conn.request('GET', '/magic/JSON/' + question)
        response = conn.getresponse()
        result = json.loads(response.read())

        await ctx.send(content=result['magic']['answer'])

    @commands.command(name='me')
    @commands.is_owner()
    async def me(self, ctx):
        await ctx.send(f'Hello {ctx.author.mention}. This command can only be used by you!')

    # @commands.command(name='me')
    # @commands.is_owner()
    # async def only_me(self, ctx):
    #     '''A simple command which only responds to the owner of the bot.'''
    #
    #     await ctx.send(f'Hello {ctx.author.mention}. This command can only be used by you!!')
    #
    # @commands.command(
    #     name='embeds',
    #     description='Tests embeds',
    #     aliases=['embeds']
    # )
    # # @commands.guild_only()
    # async def example_embed(self, ctx):
    #     '''A simple command which showcases the use of embeds.
    #     Have a play around and visit the Visualizer.'''
    #
    #     embed = discord.Embed(title='Example Embed',
    #                           description='Showcasing the use of Embeds...\nSee the visualizer for more info.',
    #                           colour=0x98FB98)
    #     embed.set_author(name='xd',
    #                      url='https://gist.github.com/MysterialPy/public',
    #                      icon_url='http://i.imgur.com/ko5A30P.png')
    #     embed.set_image(url='https://cdn.discordapp.com/attachments/84319995256905728/252292324967710721/embed.png')
    #
    #     embed.add_field(name='Embed Visualizer', value='[Click Here!](https://leovoel.github.io/embed-visualizer/)')
    #     embed.add_field(name='Command Invoker', value=ctx.author.mention)
    #     embed.set_footer(text='Made in Python with discord.py@rewrite', icon_url='http://i.imgur.com/5BFecvA.png')
    #
    #     await ctx.send(content='**A simple Embed for discord.py@rewrite in cogs.**', embed=embed)


def setup(bot):
    bot.add_cog(Basic(bot))

# from discord.ext import commands
# from datetime import datetime as d
#
#
# class Basic(commands.Cog):
#
#     def __init__(self, bot):
#         self.bot = bot
#
#     # Define a new command
#     @commands.command(
#         name='ping',
#         description='The ping command',
#         aliases=['p']
#     )
#     async def ping_command(self, ctx):
#         start = d.timestamp(d.now())
#         # Gets the timestamp when the command was used
#
#         msg = await ctx.send(content='Pinging')
#         # Sends a message to the user in the channel the message with the command was received.
#         # Notifies the user that pinging has started
#
#         await msg.edit(content=f'Pong!\nOne message round-trip took {(d.timestamp(d.now()) - start) * 1000}ms.')
#         # Ping completed and round-trip duration show in ms
#         # Since it takes a while to send the messages, it will calculate how much time it takes to edit an message.
#         # It depends usually on your internet connection speed
#
#         return
#
#     @commands.command(
#         name='say',
#         description='The say command',
#         aliases=['repeat', 'parrot'],
#         usage='<text>'
#     )
#     async def say_command(self, ctx):
#         # The 'usage' only needs to show the parameters
#         # As the rest of the format is generated automatically
#
#         # Lets see what the parameters are: -
#         # The self is just a regular reference to the class
#         # ctx - is the Context related to the command
#         # For more reference - https://discordpy.readthedocs.io/en/rewrite/ext/commands/api.html#context
#
#         # Next we get the message with the command in it.
#         msg = ctx.message.content
#
#         # Extracting the text sent by the user
#         # ctx.invoked_with gives the alias used
#         # ctx.prefix gives the prefix used while invoking the command
#         prefix_used = ctx.prefix
#         alias_used = ctx.invoked_with
#         text = msg[len(prefix_used) + len(alias_used):]
#
#         # Next, we check if the user actually passed some text
#         if text == '':
#             # User didn't specify the text
#
#             await ctx.send(content='You need to specify the text!')
#
#             pass
#         else:
#             # User specified the text.
#
#             await ctx.send(content=f'> {text}')
#
#             pass
#
#         return
#
#
# def setup(bot):
#     bot.add_cog(Basic(bot))
#     # Adds the Basic commands to the bot
#     # Note: The 'setup' function has to be there in every cog file

import os
import re
import ast
import discord
from discord.ext import commands
from discord.ext.commands import Bot

from cogs.music import Music
from cogs.moop import Moop
from util.soy import soy
from util.now import now

# TODO change moop from a client to a proper bot
# TODO implement cogs
# TODO build custom print method that returns to both the terminal and to a specific 'terminal' channel on discord
# TODO add proper logging
# TODO add youtube queueing
# TODO keep working on adding new overlays for moops
# TODO make some hilarious rich presence meme
# TODO the code is definitely 100% going to require a refactor after adding the youtube functionality
def main():
    prefix = ','
    bot = commands.Bot(command_prefix=commands.when_mentioned_or(prefix))

    shitmoop = 811211114699292672

    # TODO slim this down, a lot of these don't need to be private
    # import constant values, using environ.json if local or os.environ in repl.it
    try:
        sunday = os.environ['SUNDAYID']
        uuupah = os.environ['UUUPAHID']
        token = os.environ['TOKEN']
        # moop250 = os.environ['250MOOP'] #TODO remove from environ
        # id = os.environ['CLIENTID'] #TODO remove from environ
    except:
        try:
            file = open("environ.json", "r")
            contents = file.read()
            environ = ast.literal_eval(contents)
            file.close()

            sunday = environ['sunday']
            uuupah = environ['uuupah']
            token = environ['token']
            # moop250 = environ['moop250']
            # id = environ['id'] # as above
        except:
            print(
                f'$$ A problem has occurred during constant variable loading {now()}    '
            )   

    # startup message
    @bot.event  
    async def on_ready():
        print(f'$$ logged in as {bot.user} {now()}')
        await bot.wait_until_ready()
        dad = await bot.fetch_user(int(uuupah))
        await dad.send(
            f'hello (test) father, i have returned from the void of nonexistence {now()}')
        await bot.change_presence(activity=discord.Game(f'{prefix}help'))

    # TODO actual error handling
    # handle all functionality that is not a command
    @bot.event
    async def on_message(msg):
        await bot.process_commands(msg)

        # ignore messages sent by bot
        if msg.author == bot.user:
            return

        # print messages for terminal viewing
        print(msg.author)
        print(f' > {msg.content}')

        # sunday botherer
        if msg.author.id == int(sunday) and msg.content.lower() == 'me':
            await msg.add_reaction(f'<:moop:{shitmoop}>')
            return

        # react to moops
        if re.search(r'moo+p', msg.content, flags=re.IGNORECASE):
            await msg.add_reaction(f'<:moop:{shitmoop}>')
            return

        # watch for messages that ping the bot
        # TODO keep animation on gifs and apngs
        if f'<@!{bot.user.id}>' in msg.content or f'<@{bot.user.id}>' in    msg.content:
            await soy(msg)

    bot.add_cog(Music(bot))
    bot.add_cog(Moop(bot, uuupah))
    bot.run(token)

if __name__ == "__main__":
    main()
    
# naughty code jail

###

# if msg.author.id == int(uuupah):
# await msg.add_reaction(f'<:moop:{moop250}>')
# await msg.channel.send(f'<:moop:{moop250}>')
# return

# if msg.author.id == int(sunday):
#     await message.add_reaction('\N{AUBERGINE}')
#     return

###

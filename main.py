import os
import sys
import io
import re
import requests
import ast
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.abc import PrivateChannel
# from discord import Intents
import pytz
from datetime import datetime
from PIL import Image as image
import youtube_dl
import asyncio

from cogs.music import Music
from cogs.moop import Moop

# TODO change moop from a client to a proper bot
# TODO implement cogs
# TODO build custom print method that returns to both the terminal and to a specific 'terminal' channel on discord
# TODO add proper logging
# TODO see if the moop ping can be done programmatically instead of saving an id
# TODO chop up moop into multiple files for better organisation
# TODO set up obsidian and PARA notes for this project
# TODO link in youtube functionality
# TODO update requirements file to support above youtube functionality
# TODO keep working on adding new overlays for moops
# TODO make some hilarious rich presence meme
# TODO the code is definitely 100% going to require a refactor after adding the youtube functionality


def now():
    tz = pytz.timezone('AUSTRALIA/Adelaide')
    return datetime.now(tz).strftime("-%H.%M.%S %d.%m.%y")

# client = discord.Client()
bot = commands.Bot(command_prefix=commands.when_mentioned_or(","))

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
            f'$$ A problem has occurred during constant variable loading {now()}'
        )

# load in images
overlay = image.open('assets/a.png')
overlay_l = image.open('assets/left.png')
overlay_r = image.open('assets/right.png')


# startup message
@bot.event
async def on_ready():
    print(f'$$ logged in as {bot.user} {now()}')
    await bot.wait_until_ready()
    dad = await bot.fetch_user(int(uuupah))
    await dad.send(
        f'hello father, i have returned from the void of nonexistence {now()}')

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
    if f'<@!{bot.user.id}>' in msg.content or f'<@{bot.user.id}>' in msg.content:
        await soy(msg)


async def soy(msg):
    print(f'$$ Bot pinged, searching for images {now()}')
    async for message in msg.channel.history(limit=20):
        if message.attachments:
            # TODO iterate through files if the end isnt an image
            if message.attachments[len(message.attachments) -
                                   1].content_type.startswith("image/"):
                print(
                    f'$$ Image found at {message.attachments[len(message.attachments)-1].url} {now()}'
                )

                backgr = image.open(
                    requests.get(message.attachments[len(message.attachments) -
                                                     1].url,
                                 stream=True).raw)
                backgr_w = backgr.size[0]  # background width
                backgr_h = backgr.size[1]  # background height

                # get aspect ratios
                backgr_ar = backgr.size[0] / backgr.size[1]
                overlay_ar = overlay.size[0] / overlay.size[1]

                print(f'$$ Generating new image with overlay {now()}')

                # if backgr image is wider than original overlay, split the image and paste the halves separately
                if backgr_ar > overlay_ar:
                    # scale images to height of backgr image, preserving aspect ratio
                    l_h_ratio = (
                        backgr_h / float(overlay_l.size[1])
                    )  # get ratio of current height to background height
                    l_w_target = int(
                        (float(overlay_l.size[0]) * float(l_h_ratio)
                         ))  # get target width using current width and ratio
                    t_overlay_l = overlay_l.resize((l_w_target, backgr_h),
                                                   image.ANTIALIAS)  # resize

                    backgr.paste(t_overlay_l,
                                 (0, backgr.size[1] - t_overlay_l.size[1]),
                                 t_overlay_l)

                    r_h_ratio = (backgr_h / float(overlay_r.size[1]))
                    r_w_target = int(
                        (float(overlay_r.size[0]) * float(r_h_ratio)))
                    t_overaly_r = overlay_r.resize((r_w_target, backgr_h),
                                                   image.ANTIALIAS)

                    backgr.paste(t_overaly_r,
                                 (backgr.size[0] - t_overaly_r.size[0],
                                  backgr.size[1] - t_overaly_r.size[1]),
                                 t_overaly_r)
                # otherwise, just do it the easy way
                else:
                    # scale image to width of background image and paste at bottom
                    w_ratio = (backgr_w / float(overlay.size[0]))
                    h_target = int((float(overlay.size[1]) * float(w_ratio)))
                    t_overlay = overlay.resize((backgr_w, h_target),
                                               image.ANTIALIAS)

                    backgr.paste(t_overlay,
                                 (0, backgr.size[1] - t_overlay.size[1]),
                                 t_overlay)

                print(f'$$ New image generation complete {now()}')

                # post image
                with io.BytesIO() as image_binary:
                    backgr.save(image_binary, 'PNG', optimize=True, quality=90)
                    image_binary.seek(0)
                    await message.channel.send(file=discord.File(
                        fp=image_binary, filename='image.png'))

                print(f'$$ Reaction image posted {now()}')
                return

    print(f'$$ no images found {now()}')
    await msg.channel.send(f'<:moop:{shitmoop}>')
    return

bot.add_cog(Music(bot))
bot.add_cog(Moop(bot, uuupah))
bot.run(token)

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
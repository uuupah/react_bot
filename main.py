import os
import sys
import io
import re
import requests
import ast
import discord
import pytz
import json
import random
from datetime import datetime
from PIL import Image as image
from discord.utils import get

# import youtube_dl
# import asyncio

def now():
  tz = pytz.timezone('AUSTRALIA/Adelaide')
  return datetime.now(tz).strftime("-%H.%M.%S %d.%m.%y")

client = discord.Client()

shitmoop = 811211114699292672

# import constant values, using environ.json if local or os.environ in repl.it
try:
    sunday = os.environ['SUNDAYID']
    uuupah = os.environ['UUUPAHID']
    token = os.environ['TOKEN']
    moop250 = os.environ['250MOOP']
    id = os.environ['CLIENTID']
except:
    try:
        file = open("environ.json", "r")
        contents = file.read()
        environ = ast.literal_eval(contents)
        file.close()

        sunday = environ['sunday']
        uuupah = environ['uuupah']
        token = environ['token']
        moop250 = environ['moop250']
        id = environ['id']
    except:
        print(f'$$ A problem has occurred during constant variable loading {now()}')

# load in images
overlay = image.open('assets/a.png')
overlay_l = image.open('assets/left.png')
overlay_r = image.open('assets/right.png')

def load_query_reaction_pairs (filename) :
    if os.path.isfile('./' + str(filename)):
        with open(str(filename), 'r') as reaction_queries_file:
            return json.load(reaction_queries_file)
    else:
        return None

# load in reaction queries json
query_reaction_pairs = load_query_reaction_pairs("assets/reaction-queries.json")

# startup message
@client.event
async def on_ready():
    print(f'$$ logged in as {client.user} {now()}')
    await client.wait_until_ready()
    dad = await client.fetch_user(int(uuupah))
    await dad.send(f'hello father, i have returned from the void of nonexistence {now()}')

#TODO actual error handling
# watching for message events
@client.event
async def on_message(msg):
    # ignore messages sent by bot
    if msg.author == client.user:
        return

    # restart on certain command
    if msg.author.id == int(uuupah) and msg.content.lower() == 'moop, please restart':
        await msg.channel.send('okay, restarting')
        os.system("sh $HOME/moop.sh &")
        sys.exit()
        return

    # print messages for terminal viewing
    print(msg.author)
    print(f' > {msg.content}')

    if query_reaction_pairs != None:
        for pair in query_reaction_pairs:
            for query in pair['queries']:
                if re.search(query, msg.content, flags=re.IGNORECASE):
                    reactions = pair["reactions"]
                    reaction = reactions[random.randrange(len(reactions))]
                    reaction_id = get(client.get_all_emojis(), name=reaction)

                    await msg.add_reaction(reaction_id)
                    return

    #HORSE PLINKO
    if msg.content == 'horse plinko':
        if msg.channel.type != 'private':
            await msg.delete()
        await msg.channel.send(files=[discord.File('./assets/horse1.gif'),discord.File('./assets/horse2.gif')])
        return

    # ping
    if msg.content == '$ping':
        await msg.channel.send('pong')
        return

    if msg.author.id == int(sunday) and msg.content.lower() == 'me':
        await msg.add_reaction(f'<:moop:{shitmoop}>')
        return

    if re.search(r'moo+p', msg.content, flags=re.IGNORECASE):
      await msg.add_reaction(f'<:moop:{shitmoop}>')
      return

    # watch for messages that ping the bot
    #TODO keep animation on gifs and apngs
    if f'<@!{id}>' in msg.content or f'<@{id}>' in msg.content:
        print(f'$$ Bot pinged, searching for images {now()}')
        imageposted = False
        async for message in msg.channel.history(limit=20):
            if message.attachments:
                #TODO iterate through files if the end isnt an image
                if message.attachments[len(message.attachments)-1].content_type.startswith("image/"):
                    print(f'$$ Image found at {message.attachments[len(message.attachments)-1].url} {now()}')

                    backgr = image.open(requests.get(message.attachments[len(message.attachments)-1].url, stream=True).raw)
                    backgr_w = backgr.size[0] # background width
                    backgr_h = backgr.size[1] # background height

                    # get aspect ratios
                    backgr_ar = backgr.size[0]/backgr.size[1]
                    overlay_ar = overlay.size[0]/overlay.size[1]

                    print(f'$$ Generating new image with overlay {now()}')

                    # if backgr image is wider than original overlay, split the image and paste the halves separately
                    if backgr_ar > overlay_ar:
                      #scale images to height of backgr image, preserving aspect ratio
                      l_h_ratio = (backgr_h/float(overlay_l.size[1]))                         # get ratio of current height to background height
                      l_w_target = int((float(overlay_l.size[0])*float(l_h_ratio)))           # get target width using current width and ratio
                      t_overlay_l = overlay_l.resize((l_w_target, backgr_h), image.ANTIALIAS) # resize

                      backgr.paste(t_overlay_l, (0,backgr.size[1]-t_overlay_l.size[1]), t_overlay_l)

                      r_h_ratio = (backgr_h/float(overlay_r.size[1]))
                      r_w_target = int((float(overlay_r.size[0])*float(r_h_ratio)))
                      t_overaly_r = overlay_r.resize((r_w_target, backgr_h), image.ANTIALIAS)

                      backgr.paste(t_overaly_r, (backgr.size[0]-t_overaly_r.size[0],backgr.size[1]-t_overaly_r.size[1]), t_overaly_r)
                    # otherwise, just do it the easy way
                    else:  
                        # scale image to width of background image and paste at bottom
                        w_ratio = (backgr_w/float(overlay.size[0]))
                        h_target = int((float(overlay.size[1])*float(w_ratio)))
                        t_overlay = overlay.resize((backgr_w,h_target), image.ANTIALIAS)

                        backgr.paste(t_overlay, (0,backgr.size[1]-t_overlay.size[1]),t_overlay)

                    print(f'$$ New image generation complete {now()}')

                    # post image
                    with io.BytesIO() as image_binary:
                      backgr.save(image_binary, 'PNG', optimize=True, quality=90)
                      image_binary.seek(0)
                      await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))

                    print(f'$$ Reaction image posted {now()}')
                    imageposted = True
                    break

        if not imageposted:
          print(f'$$ no images found {now()}')
          await msg.channel.send(f'<:moop:{shitmoop}>')
        return

client.run(token)

# naughty code jail

###

## shamelessly copied from neuron at https://stackoverflow.com/questions/56060614/how-to-make-a-discord-bot-play-youtube-audio

# youtube_dl.utils.bug_reports_message = lambda: ''


# ytdl_format_options = {
#     'format': 'bestaudio/best',
#     'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
#     'restrictfilenames': True,
#     'noplaylist': True,
#     'nocheckcertificate': True,
#     'ignoreerrors': False,
#     'logtostderr': False,
#     'quiet': True,
#     'no_warnings': True,
#     'default_search': 'auto',
#     'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
# }

# ffmpeg_options = {
#     'options': '-vn'
# }

# ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# class YTDLSource(discord.PCMVolumeTransformer):
#     def __init__(self, source, *, data, volume=0.5):
#         super().__init__(source, volume)

#         self.data = data

#         self.title = data.get('title')
#         self.url = data.get('url')

#     @classmethod
#     async def from_url(cls, url, *, loop=None, stream=False):
#         loop = loop or asyncio.get_event_loop()
#         data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

#         if 'entries' in data:
#             # take first item from a playlist
#             data = data['entries'][0]

#         filename = data['url'] if stream else ytdl.prepare_filename(data)
#         return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

# @commands.command(pass_context=True)
# async def play(self, ctx, *, url):
#         print(url)
#         server = ctx.message.guild
#         voice_channel = server.voice_client

#         async with ctx.typing():
#             player = await YTDLSource.from_url(url, loop=self.bot.loop)
#             ctx.voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
#         await ctx.send('Now playing: {}'.format(player.title))

###

# if msg.author.id == int(uuupah):
# await msg.add_reaction(f'<:moop:{moop250}>')
# await msg.channel.send(f'<:moop:{moop250}>')
# return

# if msg.author.id == int(sunday):
#     await message.add_reaction('\N{AUBERGINE}')
#     return
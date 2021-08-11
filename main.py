import os
import discord
import requests
import io
from PIL import Image as image
import ast
from datetime import datetime
import pytz

def now():
  tz = pytz.timezone('AUSTRALIA/Adelaide')
  return datetime.now(tz).strftime("-%H.%M.%S %d.%m.%y")

client = discord.Client()

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

# startup message
@client.event
async def on_ready():
    print(f'logged in as {client.user} {now()}')

#TODO actual error handling
# watching for message events
@client.event
async def on_message(msg):
    # ignore messages sent by bot
    if msg.author == client.user:
        return

    # print messages for terminal viewing
    print(msg.author)
    print(f' > {msg.content}')

    # ping
    if msg.content == '$ping':
        await msg.channel.send('pong')
        return

    # watch for messages that ping the bot
    if msg.content == f'<@!{id}>':
        async for message in msg.channel.history(limit=10):
            if message.attachments:
                if message.attachments[0].content_type.startswith("image/"):
                    print(f'$$ Image found at {message.attachments[0].url} {now()}')

                    backgr = image.open(requests.get(message.attachments[0].url, stream=True).raw)
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
                    break
        return


client.run(token)

# naughty code jail

# if msg.author.id == int(sunday):
#   await msg.channel.send('awooga')
#   return

# if msg.author.id == int(uuupah):
# await msg.add_reaction(f'<:moop:{moop250}>')
# await msg.channel.send(f'<:moop:{moop250}>')
# return

# if msg.author.id == int(sunday):
#     await message.add_reaction('\N{AUBERGINE}')
#     return
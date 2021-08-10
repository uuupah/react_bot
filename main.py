import os
import discord
import requests
import io
from PIL import Image

# from PIL import image

client = discord.Client()
token = os.environ['TOKEN']
id = os.environ['CLIENTID']
overlay = Image.open('assets/a.png')
overlayleft = Image.open('assets/left.png')
overlayright = Image.open('assets/right.png')

@client.event
async def on_ready():
    print(f'logged in as {client.user}')

#TODO actual error handling
@client.event
async def on_message(msg):
    print(msg.content)
    # ignore messages by the bot
    if msg.author == client.user:
        return

    if msg.content == '$ping':
        await msg.channel.send('pong')

    if msg.content == f'<@!{id}>':
        async for message in msg.channel.history(limit=10):
            if message.attachments:
                if message.attachments[0].content_type.startswith("image/"):
                    targetimage = Image.open(requests.get(message.attachments[0].url, stream=True).raw)

                    targetar = targetimage.size[0]/targetimage.size[1]
                    overlayar = overlay.size[0]/overlay.size[1]

                    #TODO refactor so the variable names are less huge

                    # if target image is wider than original overlay, split the image and paste the halves separately
                    if targetar > overlayar:
                      #TODO clean this up its horrific
                      #scale left image to height of target image, preserving aspect ratio
                      baseheight = targetimage.size[1]
                      lefthpercent = (baseheight/float(overlayleft.size[1]))
                      leftwsize = int((float(overlayleft.size[0])*float(lefthpercent)))
                      templeftoverlay = overlayleft.resize((leftwsize, baseheight), Image.ANTIALIAS)

                      targetimage.paste(templeftoverlay, (0,targetimage.size[1]-templeftoverlay.size[1]), templeftoverlay)

                      #scale right image to height of target image, preserving aspect ratio
                      baseheight = targetimage.size[1]
                      righthpercent = (baseheight/float(overlayright.size[1]))
                      rightwsize = int((float(overlayright.size[0])*float(righthpercent)))
                      temprightoverlay = overlayright.resize((rightwsize, baseheight), Image.ANTIALIAS)

                      targetimage.paste(temprightoverlay, (targetimage.size[0]-temprightoverlay.size[0],targetimage.size[1]-temprightoverlay.size[1]), temprightoverlay)
                    # otherwise, just do it the easy way
                    else:  
                        # scale overlay to width of target image and paste it at the bottom     
                        basewidth = targetimage.size[0]
                        wpercent = (basewidth/float(overlay.size[0]))
                        hsize = int((float(overlay.size[1])*float(wpercent)))
                        tempoverlay = overlay.resize((basewidth,hsize), Image.ANTIALIAS)

                        targetimage.paste(tempoverlay, (0,targetimage.size[1]-tempoverlay.size[1]),     tempoverlay)

                    with io.BytesIO() as image_binary:
                      targetimage.save(image_binary, 'PNG')
                      image_binary.seek(0)
                      await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))

                    break

        # await msg.channel.send('awooga')
        return


client.run(token)

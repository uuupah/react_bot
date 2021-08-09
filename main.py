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


@client.event
async def on_ready():
    print(f'logged in as {client.user}')


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
                    # targetimage = message.attachments[0].url
                    # await msg.channel.send(message.attachments[0].url)
                    targetImage = Image.open(requests.get(message.attachments[0].url, stream=True).raw)

                    print(targetImage.size)

                    # tempoverlay = overlay.thumbnail(targetImage.size,Image.ANTIALIAS)

                    # scale overlay to width of target image while respecting aspect ratio
                    basewidth = targetImage.size[0]
                    wpercent = (basewidth/float(overlay.size[0]))
                    hsize = int((float(overlay.size[1])*float(wpercent)))
                    tempoverlay = overlay.resize((basewidth,hsize), Image.ANTIALIAS)

                    targetImage.paste(tempoverlay, (0,targetImage.size[1]-tempoverlay.size[1]), tempoverlay)

                    with io.BytesIO() as image_binary:
                      targetImage.save(image_binary, 'PNG')
                      image_binary.seek(0)
                      await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))

                    break

        await msg.channel.send('awooga')
        return


client.run(token)

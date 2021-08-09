import os
import discord

# from PIL import image

client = discord.Client()
token = os.environ['TOKEN']
id = os.environ['CLIENTID']
#TODO load overlay image
# overlay = image.open('./assets/a.png')


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
        targetimage = ""

        async for message in msg.channel.history(limit=10):
            if message.attachments:
                if message.attachments[0].content_type.startswith("image/"):
                    targetimage = message.attachments[0].url
                    await msg.channel.send(targetimage)
                    break

        await msg.channel.send('hello, world')
        #TODO transform image with overlay
        #TODO post image
        return

client.run(token)

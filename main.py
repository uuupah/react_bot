import os
import discord

client = discord.Client()
token = os.environ['TOKEN']

@client.event
async def on_ready():
  print(f'logged in as {client.user}')

@client.event
async def on_message(msg):
  if msg.author == client.user:
    return

  if msg.content.startswith('$test'):
    await msg.channel.send('hello, world')

client.run(token)
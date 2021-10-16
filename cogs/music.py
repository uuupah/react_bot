import asyncio

import discord
import youtube_dl

from discord.ext import commands

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address':
    '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {'options': '-vn'}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options),
                   data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #todo
        # state class:
    #  - volume
    #  - playlist (array)
    #  - skip votes
    #  - currently playing song
    #  - function to check if current user requested the song
    # 
    # util functions
    #  - function to check if audio is playing
    #  - function to check if sender is in the same voice channel as the bot
    #  - function to check if the command sender is the song requester
    # 
    # command functions
    #  - internal command to get states (this is for handling multiple servers at once)
    # 
    #  | function                      | priority |
    #  | ----------------------------- | -------- |
    #  | "leave" current channel       | 3        |
    #  | "pause" playing audio         | 2        |
    #  | change the "volume"           | 5        |
    #  | "skip" current song           | 2        |
    #  | display the song "nowplaying" | 2        |
    #  | check the "queue"             | 3        |
    #  | "clearqueue"                  | 3        |
    #  | "jumpqueue"                   | 4        |
    #  | "play" a song                 | 1        |
    # 
    #   - leave
    	#   - check if in a channel
    	#   - if so, disconnect and clear now playing and the playlist
    #  - pause
    	#  - toggle pause state
    #  - volume
    	#  - change volume using client.source.volume
    #  - skip
    	#  - stop playing with voice_client.stop() (how does it know to play another song?)
    	#  - voting related shit that is second priority atm
    #  - now playing
    	#  - get the info from the state class and spit it out
    #  - queue
    	#  - get the info from the state class and spit it out
    #  - clearqueue
    	#  - clear the info from the state class
    #  - jumpqueue
    	#  - use list popping and inserting to shift the song around the queue array
    #  - play
    	#  - make a bunch of lame checks to check that the song can be checked
    	#  - if a song is currently being played:
    		#  - add it to the queue and bail tf out
    	#  - else
    		#  - update now playing
    		#  - clear skip votes
    		#  - after playing, grab the next item in the list and play it
    # 
        # - use something equivalent to client.play(source, after=after_playing) with an after playing function that checks if theres more shit in the queue and plays it if there is

    @commands.command()
    async def testplay(self, ctx):
        ctx.send('testplay')
        return
    # 
    # checks are done on what seems to be most commands to see if music is playing and only letting you do something if it is
    # voice_client has a shitload of super useful functions!
    # also, get rid of the join command! only join if someone's trying to play something! why the fuck else would you need to be in a voice channel!
    # priority should be the states, the util functions, then the new play functionality
    # followed by queue and clearqueue
    # followed by skip
    # followed by pause
    # followed by everything else

    @commands.command()
    async def join(self, ctx):

        if not ctx.message.author.voice:
            await ctx.send("You are not connected to a voice channel!")
            return
        else:
            channel = ctx.message.author.voice.channel
            self.queue = {}
            await ctx.send(f'Connected to ``{channel}``')

        await channel.connect()

    @commands.command()
    async def play(self, ctx, *, url):
        try:
            async with ctx.typing():
                player = await YTDLSource.from_url(url,
                                                   loop=self.bot.loop,
                                                   stream=True)
                if len(self.queue) == 0:
                    self.start_playing(ctx.voice_client, player)
                    await ctx.send(
                        f':mag_right: **Searching for** ``' + url +
                        '``\n **Now Playing:** ``{}'
                        .format(player.title) + "``")
                else:
                    self.queue[len(self.queue)] = player
                    await ctx.send(
                        f':mag_right: **Searching for** ``' + url +
                        '``\n **Added to queue:** ``{}'
                        .format(player.title) + "``")

        except:
            await ctx.send("Somenthing went wrong - please try again later!")

    def start_playing(self, voice_client, player):
        self.queue[0] = player
        i = 0
        while i < len(self.queue):
            try:
                voice_client.play(self.queue[i],
                                  after=lambda e: print('Player error: %s' % e)
                                  if e else None)
            except:
                pass
            i += 1

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    # @playthis.before_invoke
    # @yt.before_invoke
    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError(
                    "Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


# bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),
#                    description='Relatively simple music bot example')

# @bot.event
# async def on_ready():
# print(f'Logged in as {bot.user} (ID: {bot.user.id})')
# print('------')

# bot.run("token")

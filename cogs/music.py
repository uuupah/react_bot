import asyncio
import time
import discord
import youtube_dl as ytdl

from discord.ext import commands

playlist = []
skip_votes = set()
now_playing = None
volume = 1.0

FFMPEG_BEFORE_OPTS = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
"""
Command line options to pass to `ffmpeg` before the `-i`.
See https://stackoverflow.com/questions/43218292/youtubedl-read-error-with-discord-py/44490434#44490434 for more information.
Also, https://ffmpeg.org/ffmpeg-protocols.html for command line option reference.
"""

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

    def _play_song(self, client, song):
        now_playing = song
        skip_votes = set()  # clear skip votes
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(song.stream_url, before_options=FFMPEG_BEFORE_OPTS), volume=volume)

        def after_playing(err):
            if len(playlist) > 0:
                next_song = playlist.pop(0)
                self._play_song(client, next_song)
            else:
                asyncio.run_coroutine_threadsafe(client.disconnect(),
                                                 self.bot.loop)

        client.play(source, after=after_playing)

    @commands.command()
    async def play(self, ctx, *, url):
        if ctx.author.voice is not None and ctx.author.voice.channel is not None:
            channel = ctx.author.voice.channel
            try:
                video = Video(url, ctx.author)
            except ytdl.DownloadError as e:
                print(f"Error downloading video: {e}")
                await ctx.send(
                    "There was an error downloading your video, sorry.")
                return
            client = await channel.connect()
            self._play_song(client, video)

        # await ctx.send('testplay')
        # if now_playing:
        #     playlist.append(song)
        # else:
        #     await self._play_song(ctx, song)
        # return
    # 
    # checks are done on what seems to be most commands to see if music is playing and only letting you do something if it is
    # voice_client has a shitload of super useful functions!
    # also, get rid of the join command! only join if someone's trying to play something! why the fuck else would you need to be in a voice channel!
    # priority should be the states, the util functions, then the new play functionality
    # followed by queue and clearqueue
    # followed by skip
    # followed by pause
    # followed by everything else

# bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),
#                    description='Relatively simple music bot example')

# @bot.event
# async def on_ready():
# print(f'Logged in as {bot.user} (ID: {bot.user.id})')
# print('------')

# bot.run("token")

# flogged wholesale from joek
# TODO do this myself
YTDL_OPTS = {
    "default_search": "ytsearch",
    "format": "bestaudio/best",
    "quiet": True,
    "extract_flat": "in_playlist"
}

class Video:
    """Class containing information about a particular video."""

    def __init__(self, url_or_search, requested_by):
        """Plays audio from (or searches for) a URL."""
        with ytdl.YoutubeDL(YTDL_OPTS) as ydl:
            video = self._get_info(url_or_search)
            video_format = video["formats"][0]
            self.stream_url = video_format["url"]
            self.video_url = video["webpage_url"]
            self.title = video["title"]
            self.uploader = video["uploader"] if "uploader" in video else ""
            self.thumbnail = video[
                "thumbnail"] if "thumbnail" in video else None
            self.requested_by = requested_by

    def _get_info(self, video_url):
        with ytdl.YoutubeDL(YTDL_OPTS) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video = None
            if "_type" in info and info["_type"] == "playlist":
                return self._get_info(
                    info["entries"][0]["url"])  # get info for first video
            else:
                video = info
            return video

    def get_embed(self):
        """Makes an embed out of this Video's information."""
        embed = discord.Embed(
            title=self.title, description=self.uploader, url=self.video_url)
        embed.set_footer(
            text=f"Requested by {self.requested_by.name}",
            icon_url=self.requested_by.avatar_url)
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        return embed
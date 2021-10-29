import os
import sys
import discord
from discord.abc import PrivateChannel
from discord.ext import commands
from util.soy import soy as soy_cmd


class Moop(commands.Cog):
    def __init__(self, bot, dad):
        self.bot = bot
        self.dad = dad

    @commands.command()
    async def ping(self, ctx):
        """returns a 'pong' at the next available convenience"""
        await ctx.send('pong')
        return

    @commands.command()
    async def restart(self, ctx):
        """restarts moop"""
        if (ctx.message.author.id == int(self.dad)):
            await ctx.send('okay, restarting')
            os.system("sh $HOME/moop.sh &")
            sys.exit()

    @commands.command()
    async def horseplinko(self, ctx):
        """posts horse plinko"""
        if not isinstance(ctx.channel, PrivateChannel):
            await ctx.message.delete()
        await ctx.send(files=[
            discord.File('./assets/horse1.gif'),
            discord.File('./assets/horse2.gif')
        ])
        return

    @commands.command()
    async def soy(self, ctx, *argv):
        """soyjacks the latest image message"""
        if len(argv) > 0:
            await soy_cmd(ctx.message, argv[0])
        else:
            await soy_cmd(ctx.message, None)
        return
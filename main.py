from typing import AsyncIterator
import discord
import praw
import random
import asyncio
from discord.ext import commands, tasks
from discord.voice_client import VoiceClient
from yt_dlp import YoutubeDL

from random import choice
from music import music


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
    'source_address': '0.0.0.0' 
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def _init_(self, source, *, data, volume=0.5):
        super()._init_(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or AsyncIterator.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

def is_connected(ctx):
    voice_client = ctx.message.guild.voice_client
    return voice_client and voice_client.is_connected()

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='?', intents=intents)
# client.add_cog(music(client))

async def setup(bot):
    await bot.add_cog(music(bot))

asyncio.run(setup(client))

status = ['Jamming out to music!', 'Eating!', 'Finding the best memes!']
queue = []
loop = False

@client.event
async def on_ready():
    print('Bot is online!')

@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'Welcome {member.mention}!  Ready to jam out? See `?help` command for details!')

@client.command(name='ping', help='This command returns the latency')
async def ping(ctx):
    await ctx.send(f'Latency: {round(client.latency * 1000)}ms')

@client.command(name='hello', help='This command returns a random welcome message')
async def hello(ctx):
    responses = ['Hello', 'Hello, how are you?', 'Hi', 'Wasssuup!']
    await ctx.send(choice(responses))


reddit = praw.Reddit(client_id='tW8Pl6gCNCy0FDtWnB9wLA',
                     client_secret='_cjwcmw9iYLIo8u0z9tfIMXS9LZ73w',
                     user_agent='pythonpraw')

@client.command(name='meme', help='This command displays popular memes')
async def meme(ctx):
    memes_submissions = reddit.subreddit('memes').hot()
    post_to_pick = random.randint(1, 25)
    for i in range(0, post_to_pick):
        submission = next(x for x in memes_submissions if not x.stickied)

    await ctx.send(submission.url)


# client.run('ODgzMjM0NTkxMTYxMzUyMjAy.YTG-UA.fyrHlI5VE8EejkFMfkoNcIb_948')

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    async with client:
        await client.start('client-secret')

asyncio.run(main())
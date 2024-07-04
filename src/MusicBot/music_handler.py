import asyncio

import discord
import yt_dlp as youtube_dl
from discord.ext import commands

# YouTube DL configuration
youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'force-ipv4': True,
    'cachedir': False,
}

ffmpeg_options = {
    'options': '-vn -b:a 128k'
}

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
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # Take all entries if it's a playlist
            return [cls(discord.FFmpegPCMAudio(entry['url'], **ffmpeg_options), data=entry)
                    for entry in data['entries']]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return [cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)]

class MusicPlayer:
    def __init__(self, ctx):
        self.bot = ctx.bot
        self.guild = ctx.guild
        self.channel = ctx.channel
        self.cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None
        self.volume = .5
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                async with asyncio.timeout(300):  # 5 minutes
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self.guild)

            if not isinstance(source, YTDLSource):
                try:
                    source = await YTDLSource.from_url(source, loop=self.bot.loop, stream=True)
                    source = source[0]  # Take the first item if it's a list
                except Exception as e:
                    await self.channel.send(f'There was an error processing your song.\n'
                                            f'```css\n[{e}]\n```')
                    continue

            source.volume = self.volume
            self.current = source

            self.guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            await self.channel.send(f'Now playing: {source.title}')
            await self.next.wait()

            source.cleanup()
            self.current = None

    def is_playing(self):
        return self.guild.voice_client and self.guild.voice_client.is_playing()

    def destroy(self, guild):
        return self.bot.loop.create_task(self.cog.cleanup(guild))

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    def get_player(self, ctx):
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.command(name='play', help='To play song or playlist')
    async def play(self, ctx, *, url):
        if not ctx.voice_client:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                await channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                return

        async with ctx.typing():
            player = self.get_player(ctx)
            sources = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)

            if len(sources) > 1:
                await ctx.send(f'Added {len(sources)} songs from playlist to queue')
                for source in sources:
                    await player.queue.put(source)
            else:
                source = sources[0]
                await player.queue.put(source)
                if player.is_playing():
                    await ctx.send(f'Added to queue: {source.title}')
                else:
                    return

    @commands.command(name='join', help='Tells the bot to join the voice channel')
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send(f"{ctx.message.author.name} is not connected to a voice channel")
            return
        else:
            channel = ctx.message.author.voice.channel
        await channel.connect()

    @commands.command(name='pause', help='This command pauses the song')
    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @commands.command(name='resume', help='Resumes the song')
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
        else:
            await ctx.send("The bot was not playing anything before this. Use play command")

    @commands.command(name='leave', help='To make the bot leave the voice channel')
    async def leave(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
        else:
            await ctx.send("The bot is not connected to a voice channel.")

    @commands.command(name='queue', help='Shows the queue')
    async def queue(self, ctx):
        player = self.get_player(ctx)
        if player.queue.empty():
            await ctx.send('There are currently no more queued songs.')
        else:
            upcoming = list(player.queue._queue)[:10]  # Accessing the internal deque object
            fmt = '\n'.join(f'**`{i + 1}.`** {source.title}' for i, source in enumerate(upcoming))
            embed = discord.Embed(title="Upcoming Songs", description=fmt, color=discord.Color.blue())
            await ctx.send(embed=embed)

    @commands.command(name='skip', help='Skips the current song')
    async def skip(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            await ctx.send('Skipped the current song.')
        else:
            await ctx.send('The bot is not playing anything at the moment.')
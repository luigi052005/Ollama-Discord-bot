import asyncio
import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp as youtube_dl

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

def get_player(self, guild: discord.Guild):
    try:
        player = self.players[guild.id]
    except KeyError:
        player = MusicPlayer(self.bot, guild)
        self.players[guild.id] = player

    return player

class MusicPlayer:
    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild
        self.queue = asyncio.Queue()
        self.next = asyncio.Event()
        self.current = None

        self.bot.loop.create_task(self.player_loop())

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
                # Convert to YTDLSource if necessary
                try:
                    source = await YTDLSource.from_url(source, loop=self.bot.loop, stream=True)
                    source = source[0]  # Take the first item if it's a list
                except Exception as e:
                    await self.guild.system_channel.send(f'There was an error processing your song.\n'
                                                         f'```css\n[{e}]\n```')
                    continue

            self.current = source

            self.guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            await self.guild.system_channel.send(f'Now playing: {source.title}')
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

    def destroy(self, guild):
        return self.bot.loop.create_task(self.cleanup(guild))

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

    @app_commands.command(name='play', description='Play a song or playlist')
    @app_commands.describe(url='The URL of the song or playlist to play')
    async def play(self, interaction: discord.Interaction, url: str):
        # Check if the user is in a voice channel
        if not interaction.user.voice:
            await interaction.response.send_message("You need to be in a voice channel to use this command.")
            return

        # Get the user's voice channel
        voice_channel = interaction.user.voice.channel

        # Connect to the voice channel if not already connected
        if not interaction.guild.voice_client:
            try:
                await voice_channel.connect()
            except Exception as e:
                await interaction.response.send_message(
                    f"An error occurred while connecting to the voice channel: {str(e)}")
                return

        # Defer the response as audio processing might take some time
        await interaction.response.defer()

        try:
            # Get or create a player for this guild
            player = self.get_player(interaction.guild)

            # Process the URL and get the audio source(s)
            sources = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)

            if len(sources) > 1:
                # It's a playlist
                await interaction.followup.send(f'Added {len(sources)} songs from playlist to queue')
                for source in sources:
                    await player.queue.put(source)
            else:
                # It's a single song
                source = sources[0]
                await player.queue.put(source)
                if interaction.guild.voice_client.is_playing():
                    await interaction.followup.send(f'Added to queue: {source.title}')
                else:
                    # If nothing is playing, start playing the added song
                    await interaction.followup.send(f'Now playing: {source.title}')
                    await self.play_next(interaction.guild)

        except Exception as e:
            await interaction.followup.send(f"An error occurred while processing your request: {str(e)}")

    async def play_next(self, guild):
        if not guild.voice_client:
            return

        player = self.get_player(guild)
        if not player.queue.empty():
            source = await player.queue.get()
            guild.voice_client.play(source, after=lambda _: self.bot.loop.create_task(self.play_next(guild)))

    @app_commands.command(name='join', description='Join the voice channel')
    async def join(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message(f"{interaction.user.name} is not connected to a voice channel")
            return
        else:
            channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.response.send_message(f"Joined {channel.name}")

    @app_commands.command(name='pause', description='Pause the current song')
    async def pause(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client.is_playing():
            voice_client.pause()
            await interaction.response.send_message("Paused the current song.")
        else:
            await interaction.response.send_message("The bot is not playing anything at the moment.")

    @app_commands.command(name='resume', description='Resume the paused song')
    async def resume(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client.is_paused():
            voice_client.resume()
            await interaction.response.send_message("Resumed the song.")
        else:
            await interaction.response.send_message("The bot was not playing anything before this. Use the play command.")

    @app_commands.command(name='leave', description='Leave the voice channel')
    async def leave(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
            await interaction.response.send_message("Left the voice channel.")
        else:
            await interaction.response.send_message("The bot is not connected to a voice channel.")

    @app_commands.command(name='queue', description='Show the current queue')
    async def queue(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        player = self.get_player(ctx)
        if player.queue.empty():
            await interaction.response.send_message('There are currently no more queued songs.')
        else:
            upcoming = list(player.queue._queue)[:10]  # Accessing the internal deque object
            fmt = '\n'.join(f'**`{i + 1}.`** {source.title}' for i, source in enumerate(upcoming))
            embed = discord.Embed(title="Upcoming Songs", description=fmt, color=discord.Color.blue())
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name='skip', description='Skip the current song')
    async def skip(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            await interaction.response.send_message('Skipped the current song.')
        else:
            await interaction.response.send_message('The bot is not playing anything at the moment.')
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp as youtube_dl

# Configuration for YouTube-DL options
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

# Configuration for FFmpeg options
ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

# Instantiate the YouTube downloader with the specified options
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


# YouTube Download Source class using YTDL and FFmpeg
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
            # If it's a playlist, return a list of sources
            return [cls(discord.FFmpegPCMAudio(entry['url'], **ffmpeg_options), data=entry)
                    for entry in data['entries']]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return [cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)]


# Music Player class to handle music playback and queue management
class MusicPlayer:
    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild
        self.queue = asyncio.Queue()
        self.next = asyncio.Event()
        self.current = None

        # Start the player loop
        self.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                async with asyncio.timeout(300):  # Timeout if nothing happens for 5 minutes
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self.guild)

            if not isinstance(source, YTDLSource):
                # Convert to YTDLSource if necessary
                try:
                    source = await YTDLSource.from_url(source, loop=self.bot.loop, stream=True)
                    source = source[0]  # Use the first item if it's a list
                except Exception as e:
                    await self.guild.system_channel.send(f'Error processing your song:\n```css\n[{e}]\n```')
                    continue

            self.current = source

            # Play the source and notify the user
            self.guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            await self.next.wait()

            # Cleanup after playback
            source.cleanup()
            self.current = None

    def destroy(self, guild):
        return self.bot.loop.create_task(self.cleanup(guild))


# Music Cog to handle music commands and interactions
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    def get_player(self, guild: discord.Guild):
        if guild.id not in self.players:
            self.players[guild.id] = MusicPlayer(self.bot, guild)
        return self.players[guild.id]

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass
        try:
            del self.players[guild.id]
        except KeyError:
            pass

    @app_commands.command(name='play', description='Play a song or playlist from YouTube')
    async def play(self, interaction: discord.Interaction, url: str):
        if not interaction.user.voice:
            embed = discord.Embed(title="Error", description="You need to be in a voice channel to use this command.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return

        voice_channel = interaction.user.voice.channel
        if not interaction.guild.voice_client:
            try:
                await voice_channel.connect()
            except Exception as e:
                embed = discord.Embed(title="Connection Error", description=f"Error connecting to the voice channel: {e}", color=discord.Color.red())
                await interaction.response.send_message(embed=embed)
                return

        await interaction.response.defer()
        try:
            player = self.get_player(interaction.guild)
            sources = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)

            if len(sources) > 1:
                embed = discord.Embed(title="Playlist Added", description=f'Added **{len(sources)}** songs to the queue.', color=discord.Color.purple())
                await interaction.followup.send(embed=embed)
                for source in sources:
                    await player.queue.put(source)
            else:
                source = sources[0]
                await player.queue.put(source)
                description = f'Now playing: **{source.title}**' if not interaction.guild.voice_client.is_playing() else f'Added to queue: **{source.title}**'
                embed = discord.Embed(title="Player", description=description, color=discord.Color.green())
                await interaction.followup.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="Error", description=f"Error processing your request: {e}", color=discord.Color.red())
            await interaction.followup.send(embed=embed)

    # Other commands for controlling music playback
    @app_commands.command(name='pause', description='Pause the current song')
    async def pause(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client.is_playing():
            voice_client.pause()
            await interaction.response.send_message("Paused the current song.")
        else:
            await interaction.response.send_message("No song is currently playing.")

    @app_commands.command(name='resume', description='Resume the paused song')
    async def resume(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client.is_paused():
            voice_client.resume()
            await interaction.response.send_message("Resumed the song.")
        else:
            await interaction.response.send_message("Nothing was paused to resume.")

    @app_commands.command(name='leave', description='Leave the voice channel')
    async def leave(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
            await interaction.response.send_message("Left the voice channel.")
        else:
            await interaction.response.send_message("Not connected to a voice channel.")

    @app_commands.command(name='queue', description='Show the current queue')
    async def queue(self, interaction: discord.Interaction):
        player = self.get_player(interaction.guild)
        if player.queue.empty():
            embed = discord.Embed(title="Player", description='The queue is empty.', color=discord.Color.blue())
            await interaction.response.send_message(embed=embed)
        else:
            upcoming = list(player.queue._queue)[:10]
            queue_list = '\n'.join(f'**`{i + 1}.`** {source.title}' for i, source in enumerate(upcoming))
            embed = discord.Embed(title="Upcoming Songs", description=queue_list, color=discord.Color.blue())
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name='skip', description='Skip the current song')
    async def skip(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            embed = discord.Embed(title="Player", description='Skipped the current song.', color=discord.Color.blue())
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Player", description='No song is currently playing.', color=discord.Color.blue())
            await interaction.response.send_message(embed=embed)
import config
import discord
from discord.ext import commands
from discord import app_commands
from src.LLM.model_loader import pull_model
from src.MusicBot.music_handler import Music
from src.LLM.ai_handler import AI

DISCORD_TOKEN = config.DISCORD_TOKEN
intents = discord.Intents.default()
intents.typing = True
intents.message_content = True
bot = commands.Bot(command_prefix="&", intents=intents, heartbeat_timeout=240)

pull_model()

class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help", description="Available commands:", color=discord.Color.blue())

        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            command_list = [f'**`{self.get_command_signature(c)}`**\n{c.help or "No description"}' for c in filtered if not c.hidden]
            if command_list:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value="\n".join(command_list), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(title=f"{cog.qualified_name} Commands", description=cog.description or "No description", color=discord.Color.blue())
        filtered = await self.filter_commands(cog.get_commands(), sort=True)
        for command in filtered:
            if not command.hidden:
                embed.add_field(name=self.get_command_signature(command), value=command.help or "No description", inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command), description=command.help or "No description", color=discord.Color.blue())
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(title=self.get_command_signature(group), description=group.help or "No description", color=discord.Color.blue())
        filtered = await self.filter_commands(group.commands, sort=True)
        for command in filtered:
            if not command.hidden:
                embed.add_field(name=self.get_command_signature(command), value=command.help or "No description", inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    def get_command_signature(self, command):
        return f'{self.context.clean_prefix}{command.qualified_name} {command.signature}'

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    print(f'<@{bot.user.id}>')
    await bot.add_cog(AI(bot))
    music_cog = Music(bot)
    await bot.add_cog(music_cog)

    print("Syncing commands...")
    await bot.tree.sync()

@bot.event
async def on_message(message):
    print(f'{message.author}: {message.content}')
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
    else:
        mention = f'<@{bot.user.id}>'
        if isinstance(message.channel, discord.DMChannel):
            if message.author != bot.user:
                ai_cog = bot.get_cog('AI')
                await ai_cog.respond(message)
        else:
            if mention in message.content:
                if message.author != bot.user:
                    ai_cog = bot.get_cog('AI')
                    await ai_cog.respond(message)

bot.run(DISCORD_TOKEN)
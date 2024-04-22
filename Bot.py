import discord
from discord.ext import commands
import config
from pullmodel import pull_model
from generateresponse import generate_response
from history import get_history
from sendresponse import send_response

DISCORD_TOKEN = config.CONFIG["DISCORD_TOKEN"]
MODEL = config.CONFIG["MODEL"]

intents = discord.Intents.default()
intents.typing = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, heartbeat_timeout=240)

pull_model(MODEL)

DISCORD_TOKEN = config.CONFIG["DISCORD_TOKEN"]

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    print(f'<@{bot.user.id}>')

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    mention = f'<@{bot.user.id}>'
    if isinstance(message.channel, discord.DMChannel):
        if message.author != bot.user:
            await respond(message)
    else:
        if mention in message.content:
            if message.author != bot.user:
                await respond(message)

@bot.command()
async def regenerate(ctx):
    message = ctx.message
    await message.delete()
    await delete_last_bot_message(message)
    await respond(message)
@bot.command()
async def dm(ctx, user: discord.User):
    message = ctx.message
    dm = message.content.replace('!dm', '')
    dm = dm.replace(f'<@{user.id}>', '')
    dm = dm.replace(f'{user.id}', '')
    await message.delete()
    await user.send(dm)

async def respond(message):
    channel = message.channel
    ctx = await bot.get_context(message)
    message_history = []
    await get_history(message_history, ctx, bot)

    async with channel.typing():
        response = generate_response(message_history)
    await send_response(response, message)

async def delete_last_bot_message(message):
    async for message in message.channel.history(limit=config.CONFIG["HISTORY_LENGH"]):
        if message.author == bot.user:
            await message.delete()
            break

bot.run(DISCORD_TOKEN)
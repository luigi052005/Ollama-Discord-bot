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

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    print(f'<@{bot.user.id}>')

@bot.event
async def on_message(message):
    if message.content.startswith("!again"):
        await message.delete()
        print("Regenerating response...")
        async for message in message.channel.history(limit=10):
            if message.author == bot.user:
                await message.delete()
                break
        await respond(message)
    else:
        mention = f'<@{bot.user.id}>'
        if mention in message.content:
            if message.author == bot.user:
                return

            await respond(message)
        else:
            return

async def respond(message):
    channel = message.channel
    ctx = await bot.get_context(message)
    message_history = []
    await get_history(message_history, ctx, bot)

    async with channel.typing():
        response = generate_response(message_history)
    await send_response(response, message)

bot.run(DISCORD_TOKEN)
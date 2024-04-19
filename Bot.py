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
bot = commands.Bot(command_prefix="!", intents=intents, heartbeat_timeout=120)

pull_model(MODEL)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command(name="chat", description="Chat with Ollama")
async def chat(ctx):
    if ctx.author.name == bot.user.name:
        return
    if ctx.message.content == " ":
        return

    if ctx.message.attachments != []:
        image = ctx.message.attachments[0]
        print(image)
    channel = ctx.channel
    message_history = []
    await get_history(message_history ,ctx, bot)

    async with channel.typing():
        response = generate_response(message_history)
    await send_response(response, ctx)



bot.run(DISCORD_TOKEN)
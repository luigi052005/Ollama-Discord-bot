import discord
from discord.ext import commands
import config
from model_loader import pull_model
from response_generator import generate_response
from conversation_history import get_history
from response_sender import send_response

DISCORD_TOKEN = config.DISCORD_TOKEN
HISTORY_LENGTH = config.HISTORY_LENGTH
intents = discord.Intents.default()
intents.typing = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, heartbeat_timeout=240)

pull_model()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    print(f'<@{bot.user.id}>')

@bot.event
async def on_message(message):
    if bot.command_prefix in message.content:
        await bot.process_commands(message)
    else:
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

@bot.command()
async def deletelastmessage(ctx):
   message = ctx.message
   await delete_last_bot_message(message)
   if isinstance(message.channel, discord.DMChannel):
       return
   await message.delete()

async def respond(message):
    ctx = await bot.get_context(message)
    message_history = []
    await get_history(message_history, ctx, bot)

    async with message.channel.typing():
        response = generate_response(message_history)
    print(response)
    await send_response(response, message)

async def delete_last_bot_message(message):
    async for message in message.channel.history(limit=HISTORY_LENGTH):
        if message.author == bot.user:
            await message.delete()
            break

bot.run(DISCORD_TOKEN)
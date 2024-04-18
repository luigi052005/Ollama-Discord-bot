import discord
from discord.ext import commands
import ollama

DISCORD_TOKEN = 'DISCORD_TOKEN'
MODEL = "mistral"

intents = discord.Intents.default()
intents.typing = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, heartbeat_timeout=60)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command(name="chat", description="Chat with Ollama")
async def chat(ctx):
    if ctx.author.name == bot.user.name:
        return

    if ctx.message.content == " ":
         return

    channel = ctx.channel
    message_history = []

    async for message in channel.history(limit=10):
        if message.author == bot.user:
            message_history.append({'role': 'assistant', 'content': message.content})
        else:
            message_history.append({'role': 'user', 'content': message.content[len('!chat'):]})

    system_message = {'role': 'system', 'content': "You are an artificial intelligence assistant. You give helpful, detailed, and polite answers to the user's questions."}
    message_history.append(system_message)
    message_history.reverse()

    print(message_history)

    async with channel.typing():
        response = generate_response(message_history)

    if response:
        if len(response) > 2000:
            print("The response was too long and has been truncated.")
            chunks = [response[i:i + 2000] for i in range(0, len(response), 2000)]
            for chunk in chunks:
                await ctx.channel.send(chunk)
        else:
            await ctx.channel.send(response)
    else:
        print("Failed to get response.")

def generate_response(message_history):
    response = ollama.chat(
        model=MODEL,
        messages=message_history,
        options={
            'num_predict': 768,
        }
    )
    return response['message']['content']

bot.run(DISCORD_TOKEN)
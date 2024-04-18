import discord
import ollama

TOKEN = 'Discord Bot Token'
MODEL = "mistral"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!ai'):
        user_input = message.content[len('!ai'):].strip()
        if user_input == " ":
            return

        channel = message.channel
        message_history = []

        async for msg in channel.history(limit=10):
            if msg.author == client.user:
                message_history.append({'role': 'assistant', 'content': msg.content})
            else:
                message_history.append({'role': 'user', 'content': msg.content})

        system_message = {'role': 'system', 'content': "A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions."}
        message_history.append(system_message)
        message_history.reverse()

        print(message_history)

        response = generate_response(message_history)
        if response:
            if len(response) > 2000:
                print("The response was too long and has been truncated.")
                chunks = [response[i:i + 2000] for i in range(0, len(response), 2000)]
                for chunk in chunks:
                    await message.channel.send(chunk)
            else:
                await message.channel.send(response)
        else:
            print("Failed to get response.")

def generate_response(message_history):
    response = ollama.chat(
        model=MODEL,
        messages=message_history,
        options={
            'num_predict': 768,
        },
    )
    return response['message']['content']

client.run(TOKEN)
import config
import time
import discord
from discord.ext import commands
from src.LLM.model_loader import pull_model
from src.LLM.response_generator import generate_response
from src.LLM.conversation_history import get_history
from src.LLM.response_sender import send_response

HISTORY_LENGTH = config.HISTORY_LENGTH

pull_model()

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='regenerate', help='Regenerates the last bot message')
    async def regenerate(self, ctx):
        message = ctx.message
        await message.delete()
        await self.delete_last_bot_message(message)
        await self.respond(message)

    @commands.command(name='dm', help='Can be used to dm a user on the server', hidden=True)
    async def dm(self, ctx, user: discord.User):
        message = ctx.message
        dm = message.content.replace('!dm', '')
        dm = dm.replace(f'<@{user.id}>', '')
        dm = dm.replace(f'{user.id}', '')
        await message.delete()
        await user.send(dm)

    @commands.command(name='deletelastmessage', help='Deletes the last bot message')
    async def deletelastmessage(self, ctx):
        message = ctx.message
        await self.delete_last_bot_message(message)
        if not isinstance(message.channel, discord.DMChannel):
            await message.delete()

    @commands.command(name='panic', help='Deletes the last bot message', hidden=True)
    async def panic(self, ctx):
        message = ctx.message
        await self.delete_all_messages(message)
        if not isinstance(message.channel, discord.DMChannel):
            await message.delete()

    async def respond(self, message):
        ctx = await self.bot.get_context(message)
        message_history = []
        await get_history(message_history, ctx, self.bot)

        async with message.channel.typing():
            response = generate_response(message_history)

        await send_response(response, message)

    async def delete_last_bot_message(self, message):
        async for message in message.channel.history(limit=HISTORY_LENGTH):
            if message.author == self.bot.user:
                await message.delete()
                break

    async def delete_all_messages(self, message):
        async for message in message.channel.history(limit=HISTORY_LENGTH):
            if message.author == self.bot.user:
                time.sleep(0.6)
                await message.delete()
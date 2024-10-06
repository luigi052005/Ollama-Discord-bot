import config
import time
import discord
from discord import app_commands
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

    @app_commands.command(name='regenerate', description='Regenerates the last bot message')
    async def regenerate(self, interaction: discord.Interaction):
        message_history = []
        channel = interaction.channel
        await self.delete_last_bot_message(channel)
        # respond
        await get_history(message_history, channel, self.bot)
        await interaction.response.defer()
        async with channel.typing():
            response = await generate_response(message_history)

        await interaction.followup.send(response)


    @commands.command(name='dm', help='Can be used to dm a user on the server', hidden=True)
    async def dm(self, ctx, user: discord.User):
        message = ctx.message
        dm = message.content.replace('&dm', '')
        dm = dm.replace(f'<@{user.id}>', '')
        dm = dm.replace(f'{user.id}', '')
        await message.delete()
        await user.send(dm)

    @app_commands.command(name='deletelastmessage', description='Deletes the last bot message')
    async def deletelastmessage(self, interaction: discord.Interaction):
        channel = interaction.channel
        await self.delete_last_bot_message(channel)
        if not isinstance(channel, discord.DMChannel):
            await interaction.response.defer()

    @commands.command(name='clear', help='Deletes all bot message', hidden=True)
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
            response = await generate_response(message_history)
        await send_response(response, message.channel)

    async def delete_last_bot_message(self, channel):
        async for message in channel.history(limit=HISTORY_LENGTH):
            if message.author == self.bot.user:
                await message.delete()
                break

    async def delete_all_messages(self, message):
        async for message in message.channel.history(limit=HISTORY_LENGTH):
            if message.author == self.bot.user:
                time.sleep(0.6)
                await message.delete()
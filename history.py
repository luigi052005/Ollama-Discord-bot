import config
from getattachments import get_attachments

async def get_history(message_history, ctx, bot):
    async for message in ctx.history(limit=10):
        image_base64 = None
        txt = None
        #add bot message to history
        if message.author == bot.user:
            message_history.append({'role': 'assistant', 'content': message.content})
        #add user message to history
        if message.author != bot.user:
            if message.attachments:
                image_base64, txt = await get_attachments(message, bot, image_base64, txt)
            user_message = message.content.replace(f'<@{bot.user.id}>', '')
            message_history.append({
                'role': 'user',
                'content':f"{message.author.name}: {user_message} {[txt] if txt else ""}",
                'images': [image_base64] if image_base64 else []
            })

    system_message = {'role': 'system', 'content': config.CONFIG['SYSTEM']}
    message_history.append(system_message)
    message_history.reverse()
    print(message_history)
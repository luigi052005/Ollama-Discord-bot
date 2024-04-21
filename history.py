import config
from getattachments import get_attachments

async def get_history(message_history, ctx, bot):
    async for message in ctx.history(limit=config.CONFIG["HISTORY_LENGH"]):
        image_base64 = None
        plain_text = None
        #add bot message to history
        if message.author == bot.user:
            message_history.append({'role': 'assistant', 'content': message.content})
        #add user message to history
        if message.author != bot.user:
            mention = f'<@{bot.user.id}>'
            #if message.content != mention:
            if message.attachments:
                image_base64, plain_text = await get_attachments(message, bot, image_base64, plain_text)
            user_message = message.content.replace(f'<@{bot.user.id}>', '')
            message_history.append({
                'role': 'user',
                'content':f"{message.created_at} {message.author.name}: {user_message} {[plain_text] if plain_text else ""}",
                'images': [image_base64] if image_base64 else []
            })

    system_message = {'role': 'system', 'content': config.CONFIG['SYSTEM']}
    message_history.append(system_message)
    message_history.reverse()
    print(message_history)
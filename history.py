import pytz
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
            user_message = message.content.replace(f'<@{bot.user.id}>', f'@{bot.user.name}')
            timestamp = message.created_at
            local_tz = pytz.timezone(config.CONFIG["LOCAL_TIMEZONE"])
            local_time = timestamp.astimezone(local_tz)
            timestamp = local_time.strftime('%Y-%m-%d %H:%M:%S')
            #get message attachments
            if message.attachments:
                image_base64, plain_text = await get_attachments(message, bot, image_base64, plain_text)
            message_history.append({
                'role': 'user',
                'content':f"{timestamp} {message.author.name}: {user_message} {[plain_text] if plain_text else ""}",
                'images': [image_base64] if image_base64 else []
            })

    system_message = {'role': 'system', 'content': config.CONFIG['SYSTEM']}
    message_history.append(system_message)
    message_history.reverse()
    print(message_history)
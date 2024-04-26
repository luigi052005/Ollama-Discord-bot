import pytz
import config
from attachment_handler import get_attachments

HISTORY_LENGTH = config.HISTORY_LENGTH
LOCAL_TIMEZONE = config.LOCAL_TIMEZONE
SYSTEM = config.SYSTEM

async def get_history(message_history, ctx, bot):
    async for message in ctx.history(limit=config.HISTORY_LENGTH):
        image_base64 = None
        text_files = []
        #add bot message to history
        if message.author == bot.user:
            if not message.content.strip():
                return
            message_history.append({'role': 'assistant', 'content': message.content})
        #add user message to history
        if message.author != bot.user:
            user_message = message.content.replace(f'<@{bot.user.id}>', f'@{bot.user.name}')
            timestamp = message.created_at
            local_tz = pytz.timezone(LOCAL_TIMEZONE)
            local_time = timestamp.astimezone(local_tz)
            timestamp = local_time.strftime('%Y-%m-%d %H:%M:%S')
            #get message attachments
            if message.attachments:
                image_base64, text_files = await get_attachments(message, bot, image_base64, text_files)
            message_history.append({
                'role': 'user',
                'content':f"{timestamp} {message.author.name}: {user_message} {[text_files] if text_files else ''}",
                'images': [image_base64] if image_base64 else []
            })

    system_message = {'role': 'system', 'content': SYSTEM}
    message_history.append(system_message)
    message_history.reverse()
    print(message_history)

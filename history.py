import config
from encodeimage import encode_image

async def get_history(message_history, channel, bot):
        async for message in channel.history(limit=10):
            #add bot message to history
            if message.author == bot.user:
                message_history.append({'role': 'assistant', 'content': message.content})
            #add user message to history
            if message.content[len('!chat'):] != "":
                image_base64 = None
                if message.attachments:
                    url = message.attachments[0].url
                    image_base64 = await encode_image(image_base64, message, url)
                message_history.append({'role': 'user', 'content': message.content[len('!chat'):], "images": ([image_base64] if image_base64 else [])})

        system_message = {'role': 'system', 'content': config.CONFIG['SYSTEM']}
        message_history.append(system_message)
        message_history.reverse()
        print(message_history)
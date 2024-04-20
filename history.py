import config
from encodeimage import encode_image
from txtcontent import  txt_content
from getattachments import get_attachments

async def get_history(message_history, ctx, bot):
    async for message in ctx.history(limit=10):
        image_base64 = None
        content = None
        #add bot message to history
        if message.author == bot.user:
            message_history.append({'role': 'assistant', 'content': message.content})
        #add user message to history
        if message.author != bot.user:
            if message.attachments:
                image_base64, content = await get_attachments(message, bot, image_base64, content)
                #for attachment in message.attachments:
                    #image_base64 = None
                    #content = None
                    #if message.content[len(f'<@{bot.user.id}>'):] != "":
                        #if attachment.content_type.startswith('image/'):
                            #url = attachment.url
                            #image_base64 = await encode_image(url)
                        #elif attachment.content_type.endswith(('.txt')):
                            #url = attachment.url
                            #content = await txt_content(url)
                            #print("CONTENT:", content)
            message_history.append({
                'role': 'user',
                'content':f"{message.author.name}:{message.content[len(f'<@{bot.user.id}>'):]}{[content] if content else ""}",
                'images': [image_base64] if image_base64 else []
            })

    system_message = {'role': 'system', 'content': config.CONFIG['SYSTEM']}
    message_history.append(system_message)
    message_history.reverse()
    print(message_history)
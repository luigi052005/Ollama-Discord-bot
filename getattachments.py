from encodeimage import encode_image
from txtcontent import  txt_content

async def get_attachments(message, bot, image_base64, plain_text):
    for attachment in message.attachments:
        if message.content[len(f'<@{bot.user.id}>'):] != "":
            print(attachment.content_type)
            if attachment.content_type.startswith('image/'):
                url = attachment.url
                image_base64 = await encode_image(url)
            elif attachment.content_type.startswith(('text')):
                url = attachment.url
                plain_text = await txt_content(url)

            return image_base64, plain_text
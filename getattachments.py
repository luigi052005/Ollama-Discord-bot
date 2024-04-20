from encodeimage import encode_image
from txtcontent import  txt_content

async def get_attachments(message, bot, image_base64, txt):
    for attachment in message.attachments:
        if message.content[len(f'<@{bot.user.id}>'):] != "":
            print(attachment.content_type)
            if attachment.content_type.startswith('image/'):
                url = attachment.url
                image_base64 = await encode_image(url)
            elif attachment.content_type.startswith(('text', "application/vnd.openxmlformats")):
                url = attachment.url
                txt = await txt_content(url)

            return image_base64, txt
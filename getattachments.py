from encodeimage import encode_image
from txtcontent import  txt_content

async def get_attachments(message, bot, image_base64, content):
    for attachment in message.attachments:
        if message.content[len(f'<@{bot.user.id}>'):] != "":
            if attachment.content_type.startswith('image/'):
                url = attachment.url
                image_base64 = await encode_image(url)
            print(attachment.content_type)
            if attachment.content_type.startswith(('text')):
                url = attachment.url
                content = await txt_content(url)
            else:
                print("no attachments")

            return image_base64, content
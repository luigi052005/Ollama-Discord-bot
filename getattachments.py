from encodeimage import encode_image
from txtcontent import txt_content

async def get_attachments(message, bot, image_base64, plain_text):
    for attachment in message.attachments:
        #print(attachment.content_type)
        if attachment.content_type.startswith('image/'):
            url = attachment.url
            image_base64 = await encode_image(url)
        elif attachment.content_type.startswith(('text')):
            url = attachment.url
            plain_text = await txt_content(url, attachment)

        return image_base64, plain_text
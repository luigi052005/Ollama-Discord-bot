import base64
import aiohttp

async def encode_image(url):
    if url[0:26] == 'https://cdn.discordapp.com':
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                image_buffer = await resp.read()

        image_base64 = base64.b64encode(image_buffer).decode('utf-8')
        return image_base64
    else:
        return
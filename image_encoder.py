import base64
import io
from PIL import Image
import aiohttp

async def encode_image(url):
    if url[0:26] == 'https://cdn.discordapp.com':
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                image_buffer = await resp.read()

                # Convert image bytes to PNG
                image = Image.open(io.BytesIO(image_buffer))
                png_buffer = io.BytesIO()
                image.save(png_buffer, format="PNG")
                png_buffer.seek(0)

                # Encode the PNG image to base64
                image_base64 = base64.b64encode(png_buffer.getvalue()).decode('utf-8')
                return image_base64

        image_base64 = base64.b64encode(image_buffer).decode('utf-8')
        return image_base64
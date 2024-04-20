import aiohttp


async def txt_content(url):
    if url[0:26] == 'https://cdn.discordapp.com':
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                plain_text = await resp.read()
                plain_text = plain_text.decode('utf-8')
                return plain_text
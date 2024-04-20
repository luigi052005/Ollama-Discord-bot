import aiohttp


async def txt_content(url):
    if url[0:26] == 'https://cdn.discordapp.com':
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                txt = await resp.read()
                txt = txt.decode('utf-8')
                return txt
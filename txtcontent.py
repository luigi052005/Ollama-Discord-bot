import aiohttp


async def txt_content(url):
    print("called")
    if url[0:26] == 'https://cdn.discordapp.com':
        print("checked url")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                content = await resp.read()
                return content
import aiohttp

async def txt_content(url, attachment):
    if url[0:26] == 'https://cdn.discordapp.com':
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if attachment.content_type.startswith(('text')):
                    plain_text = await resp.read()
                    plain_text = plain_text.decode('utf-8')
                    print(f"PLAIN_TEXT:{plain_text}")
                    return plain_text
                if attachment.content_type.startswith(('application/pdf')):
                    pass
                    #handle pdf
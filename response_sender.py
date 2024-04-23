async def send_response(response, ctx):
    #print(response)
    if response:
        if len(response) > 2000:
            print("The response was too long and has been truncated.")
            chunks = [response[i:i + 2000] for i in range(0, len(response), 2000)]
            for chunk in chunks:
                await ctx.channel.send(chunk)
        else:
            await ctx.channel.send(response)
    else:
        print("Failed to get response.")

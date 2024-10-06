async def send_response(response, channel):
    if response:
        if len(response) > 2000:
            print("The response was too long and has been truncated.")
            chunks = [response[i:i + 2000] for i in range(0, len(response), 2000)]
            for chunk in chunks:
                await channel.send(chunk)
        else:
            await channel.send(response)
    else:
        print("Failed to get response.")


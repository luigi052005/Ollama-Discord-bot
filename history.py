import config
async def get_history(message_history, channel, bot):
        async for message in channel.history(limit=10):
            #add bot message to history
            if message.author == bot.user:
                message_history.append({'role': 'assistant', 'content': message.content})
            #add user message to history
            if message.content[len('!chat'):] != "":
                message_history.append({'role': 'user', 'content': message.content[len('!chat'):]})
                print(message.content[len('!chat'):])

        system_message = {'role': 'system', 'content': config.CONFIG['SYSTEM']}
        message_history.append(system_message)
        message_history.reverse()
        print(message_history)
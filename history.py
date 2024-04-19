import config
async def get_history(message_history, channel, bot):
        async for message in channel.history(limit=10):
            if message.author == bot.user:
                message_history.append({'role': 'assistant', 'content': message.content})
            else:
                message_history.append({'role': 'user', 'content': message.content[len('!chat'):]})

        system_message = {'role': 'system', 'content': config.CONFIG['SYSTEM']}
        message_history.append(system_message)
        message_history.reverse()
        print(message_history)
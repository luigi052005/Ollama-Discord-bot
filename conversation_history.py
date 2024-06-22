import pytz
import config
import json
from attachment_handler import get_attachments
from memory_module import LongTermMemory

memory = LongTermMemory()

HISTORY_LENGTH = config.HISTORY_LENGTH
LOCAL_TIMEZONE = config.LOCAL_TIMEZONE
SYSTEM = config.SYSTEM


async def get_history(message_history, ctx, bot):
    channel_id = str(ctx.channel.id)
    query = ctx.message.content  # Assuming the latest message is the query

    async for message in ctx.history(limit=config.HISTORY_LENGTH):
        image_base64 = None
        text_files = []
        # add bot message to history
        if message.author == bot.user:
            if not message.content.strip():
                continue
            message_history.append({'role': 'assistant', 'content': message.content})
        # add user message to history
        if message.author != bot.user:
            user_message = message.content.replace(f'<@{bot.user.id}>', f'@{bot.user.name}')
            timestamp = message.created_at
            local_tz = pytz.timezone(LOCAL_TIMEZONE)
            local_time = timestamp.astimezone(local_tz)
            timestamp = local_time.strftime('%Y-%m-%d %H:%M:%S')
            # get message attachments
            if message.attachments:
                image_base64, text_files = await get_attachments(message, bot, image_base64, text_files)
            message_history.append({
                'role': 'user',
                'content': f"{timestamp} {message.author.name}: {user_message} {[text_files] if text_files else ''}",
                'images': [image_base64] if image_base64 else []
            })

    # Retrieve and process relevant memories
    relevant_memories = memory.get_relevant_memories(channel_id, query, top_k=3, similarity_threshold=0.4)
    memory_content = ""
    if relevant_memories:
        processed_memories = process_memories(relevant_memories)
        memory_content = f"Consider this relevant information from past interactions: {processed_memories}"
        print(f"Processed memories: {memory_content}")
        print(memory_content)
    else:
        print("No relevant memories found")

    # Combine system message and memory
    system_message = {
        'role': 'system',
        'content': f"{SYSTEM}\n\n{memory_content}".strip()
    }
    message_history.append(system_message)
    message_history.reverse()

    print("Final message history:")
    print(json.dumps(message_history, indent=2))

    # Store the current interaction in memory
    memory.add_memory(channel_id,f"User: {query}\nBot: {message_history[0]['content'] if message_history else 'No response'}")
def process_memories(memories):
    processed = []
    for memory in memories:
        if "User:" in memory and "Bot:" in memory:
            user_message = memory.split("User:")[1].split("Bot:")[0].strip()
            processed.append(f"User mentioned: {user_message}")
    return "; ".join(processed)


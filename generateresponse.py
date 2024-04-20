import ollama
import config

def generate_response(message_history):
    response = ollama.chat(
        model=config.CONFIG["MODEL"],
        messages=message_history,
        options={
            'num_predict': config.CONFIG["NUM_PREDICT"],
        }
    )
    return response['message']['content']
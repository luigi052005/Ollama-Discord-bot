import ollama
import config

MODEL = config.CONFIG["MODEL"]


def generate_response(message_history):
    response = ollama.chat(
        model=MODEL,
        messages=message_history,
        options={
            'num_predict': 2048,
        }
    )
    return response['message']['content']
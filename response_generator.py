import ollama
import config

MODEL = config.MODEL

def generate_response(message_history):
    response = ollama.chat(
        model=MODEL,
        messages=message_history,
        options={
            "num_predict": 8000
        }
    )
    return response['message']['content']

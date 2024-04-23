import ollama
import config

def generate_response(message_history):
    response = ollama.chat(
        model=config.CONFIG["MODEL"],
        messages=message_history,
        options={
            "num_predict": 8000
        }
    )
    return response['message']['content']
import ollama
import config

MODEL = config.MODEL
NUM_PREDICT = config.NUM_PREDICT

def generate_response(message_history):
    while True:
        response = ollama.chat(
            model=MODEL,
            messages=message_history,
            options={
                "num_predict": NUM_PREDICT
            }
        )
        return response['message']['content']
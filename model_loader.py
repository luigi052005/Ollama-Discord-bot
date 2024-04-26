import ollama
import config

MODEL = config.MODEL

def pull_model():
    try:
        ollama.chat(MODEL)
    except ollama.ResponseError as e:
        print('Error: model not found pulling model...')
        if e.status_code == 404:
            ollama.pull(MODEL)
        else:
            return

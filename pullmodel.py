import ollama
import config

MODEL = config.CONFIG["MODEL"]

def pullmodel():
  try:
    ollama.chat(MODEL)
  except ollama.ResponseError as e:
    print('Error: model not found pulling model...')
    if e.status_code == 404:
      ollama.pull(MODEL)

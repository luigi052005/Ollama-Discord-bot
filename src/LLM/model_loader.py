import ollama
import config

MODEL = config.MODEL

def pull_model():
    try:
        ollama.chat(MODEL)
    except ollama.ResponseError as e:
        print('Error: model not found pulling model...')
        if e.status_code == 404:
            try:
                pull = ollama.pull(MODEL, stream=True)
                progress_states = set()
                for progress in pull:
                    if progress.get('status') in progress_states:
                        continue
                    progress_states.add(progress.get('status'))
                    print(progress.get('status'))
            except ollama.ResponseError as e:
                print(e)
        else:
            return
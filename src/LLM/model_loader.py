import ollama
import config
from tqdm import tqdm

MODEL = config.MODEL


def pull_model():
    try:
        ollama.chat(MODEL)
    except ollama.ResponseError as e:
        print('Error: model not found pulling model...')
        if e.status_code == 404:
            try:
                current_digest, bars = '', {}
                for progress in ollama.pull(MODEL, stream=True):
                    digest = progress.get('digest', '')
                    if digest != current_digest and current_digest in bars:
                        bars[current_digest].close()
                    if not digest:
                        print(progress.get('status'))
                        continue
                    if digest not in bars and (total := progress.get('total')):
                        bars[digest] = tqdm(total=total, desc=f'pulling {digest[7:19]}', unit='B', unit_scale=True)
                    if completed := progress.get('completed'):
                        bars[digest].update(completed - bars[digest].n)
                    current_digest = digest

                # Close any remaining progress bars
                for bar in bars.values():
                    bar.close()
            except ollama.ResponseError as e:
                print(e)
        else:
            return


if __name__ == "__main__":
    pull_model()
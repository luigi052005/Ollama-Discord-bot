# Ollama Discord Bot

A Discord Bot that utilizes the Ollama API.

## Installation

To install the necessary dependencies, execute the following command in your terminal:

```bash
pip install -r requirements.txt
```

## Getting Started

1. **Clone the Repository:** Begin by cloning this repository to your local machine.

```bash
git clone https://github.com/luigi052005/Ollama-Discord-bot
```

2. **Navigate to the Directory:** Move into the directory containing the cloned repository.

```bash
cd Ollama-Discord-Bot
```

3. **Configuration:**
   
   - Open `config.py` and enter your Discord bot token.
   
   ```python
   # config.py
   
   CONFIG = {
    'DISCORD_TOKEN': 'Token',
    'MODEL': 'llama3',
    'SYSTEM': "You are an artificial intelligence assistant. You give helpful, detailed, and polite answers to the user's questions.",
    }
   ```

4. **Run the Bot:**
   
   Execute the following command to start the bot:

```bash
python Bot.py
```

Now your Ollama Discord Bot should be up and running, ready to enhance your Discord server experience!
Ping your bot and enjoy!

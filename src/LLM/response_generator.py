import ollama
import config
from src.Tools.tools import tools
from src.Tools.get_weather import get_current_weather
from src.Tools.calculator import calculator

MODEL = config.MODEL
NUM_PREDICT = config.NUM_PREDICT

async def generate_response(message_history):
    while True:
        # Initial chat response with Ollama
        response = ollama.chat(
            model=MODEL,
            messages=message_history,
            tools=tools,
            options={
                "num_predict": NUM_PREDICT
            }
        )
        if not response['message'].get('tool_calls'):
            return response['message']['content']

        # Process function calls made by the model
        if response['message'].get('tool_calls'):
            print("USING TOOLS")
            available_functions = {
                'get_current_weather': get_current_weather,
                'calculator': calculator,
            }
            for tool in response['message']['tool_calls']:
                function_to_call = available_functions[tool['function']['name']]
                if tool['function']['name'] == 'get_current_weather':
                    function_response = await function_to_call(tool['function']['arguments']['city'])
                elif tool['function']['name'] == 'calculator':
                    args = tool['function']['arguments']
                    function_response = function_to_call(args['operation'], args['x'], args['y'])
                print(function_response)
                # Add function response to the conversation
                message_history.append(
                    {
                        'role': 'tool',
                        'content': str(function_response),
                    }
                )

            # Second API call: Get final response from the model
            final_response = ollama.chat(model=MODEL, messages=message_history)
            return final_response['message']['content']
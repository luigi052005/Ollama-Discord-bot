import ollama
import config
from src.LLM.tool_handler import check_for_tool_calls
from src.LLM.tools import execute_tool

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
        tool_response = check_for_tool_calls(response['message']['content'])
        if tool_response["tool"] is None:
            # If no tool call, send the response to the user
            return response['message']['content']
        else:
            print(f"AGENTLOOP: {response['message']['content']}")
            # Execute the tool
            tool_result = execute_tool(tool_response["tool"], tool_response["tool_input"])

            # Add tool result to message history
            message_history.append({
                "role": "system",
                "name": tool_response["tool"],
                "content": f"Tool result: {tool_result}"
            })
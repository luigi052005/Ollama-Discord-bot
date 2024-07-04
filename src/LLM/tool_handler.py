import json
import re
from typing import Dict, Any


def check_for_tool_calls(response: str) -> Dict[str, Any]:
    print("extracting tool calls...")

    # Use regex to find all JSON-like patterns in the response
    json_pattern = r'\{(?:[^{}]|\{[^{}]*\})*\}'
    potential_jsons = re.findall(json_pattern, response)

    for potential_json in potential_jsons:
        try:
            json_data = json.loads(potential_json)
            if "tool" in json_data and "tool_input" in json_data:
                print("tool calls found")
                return json_data
        except json.JSONDecodeError:
            continue

    print("no tool calls found")
    return {"tool": None, "tool_input": None}
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import operator


tools = {
    "search_web": {
        "name": "search_web",
        "description": "Search the web for information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        },
        "example": {
            "tool": "search_web",
            "tool_input": {
                "query": "latest news on artificial intelligence"
            }
        }
    },
    "calculator": {
        "name": "calculator",
        "description": "Perform basic arithmetic operations",
        "parameters": {
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["operation", "a", "b"]
            },
        "example": {
            "tool": "calculator",
            "tool_input": {
                "operation": "divide",
                "a": 854,
                "b": 63
            }
        }
    }
}

def execute_tool(tool_name: str, tool_input: Dict[str, Any]) -> str:
    if tool_name == "search_web":
        print("using tool web")
        return search_web(tool_input["query"])
    elif tool_name == "calculator":
        print("using tool calculator")
        return calculator(tool_input["operation"], tool_input["a"], tool_input["b"])
    else:
        return f"Tool {tool_name} not found"

def search_web(query: str) -> str:
    url = f"https://html.duckduckgo.com/html/?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('div', class_='result__body')

        formatted_results = []
        for result in results[:10]:  # Limit to top 10 results
            title_element = result.find('a', class_='result__a')
            snippet_element = result.find('a', class_='result__snippet')
            url_element = title_element['href'] if title_element else "N/A"
            title = title_element.text.strip() if title_element else "No Title"
            snippet = snippet_element.text.strip() if snippet_element else "No Snippet"

            formatted_results.append(f"Title: {title}\nURL: {url_element}\nSnippet: {snippet}\n")

        formatted_output = "\n".join(formatted_results) if formatted_results else "No results found."
        print(formatted_output)
        return formatted_output

    except requests.RequestException as e:
        return f"Error occurred while searching: {str(e)}"

def calculator(operation: str, a: float, b: float) -> str:
    ops = {
        'add': operator.add,
        'subtract': operator.sub,
        'multiply': operator.mul,
        'divide': operator.truediv
    }
    if operation not in ops:
        return f"Error: Unknown operation '{operation}'"
    if operation == 'divide' and b == 0:
        return "Error: Division by zero"
    result = ops[operation](a, b)
    print(f"Result of {a} {operation} {b} = {result}")
    return f"Result of {a} {operation} {b} = {result}"

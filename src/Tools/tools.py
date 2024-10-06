tools = [
    {
        'type': 'function',
        'function': {
            'name': 'get_current_weather',
            'description': 'Get the current weather for a city',
            'parameters': {
                'type': 'object',
                'properties': {
                    'city': {
                        'type': 'string',
                        'description': 'The name of the city',
                    },
                },
                'required': ['city'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'calculator',
            'description': 'Perform basic arithmetic operations',
            'parameters': {
                'type': 'object',
                'properties': {
                    'operation': {
                        'type': 'string',
                        'description': 'The arithmetic operation to perform (add, subtract, multiply, divide)',
                    },
                    'x': {
                        'type': 'number',
                        'description': 'The first number',
                    },
                    'y': {
                        'type': 'number',
                        'description': 'The second number',
                    },
                },
                'required': ['operation', 'x', 'y'],
            },
        },
    }
]
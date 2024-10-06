def calculator(operation: str, x: float, y: float) -> float:
    if operation == "add":
        return x + y
    elif operation == "subtract":
        return x - y
    elif operation == "multiply":
        return x * y
    elif operation == "divide":
        if y != 0:
            return x / y
        else:
            raise ValueError("Cannot divide by zero")
    else:
        raise ValueError("Invalid operation")
import json

def get_account_balance(account_number: str):
    if account_number == 'ABCD1234':
        return 'Rs. 5000.50'
    elif account_number == '123456789':
        return 'Rs. 12,000'
    elif account_number.startswith('0'):
        return 'INR 1 Lakh'
    else:
        return 'Invalid Account - Please try again'

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_account_balance",
            "description": "Get the current balance of a bank account",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_number": {"type": "string", "description": "Account number, e.g. 123456789"},
                },
                "required": ["account_number"],
            },
        },
    }
]

def handle_tool_calls(message: any):
    if isinstance(message, dict):
        tool_calls = message.get('tool_calls', [])
    else:
        tool_calls = message.tool_calls
    if not tool_calls:
        return
    
    tool_call = tool_calls[0]
    if isinstance(tool_call, dict):
        id = tool_call.get('id')
        function_name = tool_call.get('function', dict()).get('name')
        function_arguments = tool_call.get('function', dict()).get('arguments', '{}') 
    else:
        id = tool_call.id
        function_name = tool_call.function.name
        function_arguments = tool_call.function.arguments 
    
    args = json.loads(function_arguments)
    if function_name == 'get_account_balance':
        result = get_account_balance(args['account_number'])
    else:
        result = 'Invalid Tool Call'

    messages = []
    messages.append(
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": id,
                    "type": "function",
                    "function": {
                        "name": function_name,
                        "arguments": function_arguments,
                    },
                }
            ],
        }
    )
    messages.append(
        {
            "role": "tool",
            "tool_call_id": id,
            "content": json.dumps(result),
        }
    )

    return messages

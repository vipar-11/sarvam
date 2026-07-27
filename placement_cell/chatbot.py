from asyncio import exceptions
from asyncio import exceptions
from asyncio import exceptions
from sarvamai import SarvamAI
from openai import OpenAI
import json

# Expectets Tools to be passed in this format
# tools = [
#     {
#         "type": "function",
#         "function": {
#             "name": "get_account_balance",
#             "description": "Get the current balance of a bank account",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "account_number": {"type": "string", "description": "Account number, e.g. 123456789"},
#                 },
#                 "required": ["account_number"],
#             },
#         },
#     }
# ]

class ChatBot:

    def __init__(self, api_key: str, model: str, system_prompt: str=None, tools: list=None):
        self.client = SarvamAI(api_subscription_key=api_key)
        self.client = client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.model = model        
        self.tools = tools
        self.chat_history = [{'role': 'system', 'content': system_prompt}] if system_prompt else []
        # Dynamic tool function mappings
        self.tool_functions = {}

    def register_tool(self, name: str, func: callable):
        """
        Dynamically registers a callable function for tool execution.
        """
        self.tool_functions[name] = func
    
    def handle_tool_calls(self, message: any):
        if isinstance(message, dict):
            tool_calls = message.get('tool_calls', [])
        else:
            tool_calls = message.tool_calls
        if not tool_calls:
            return
        
        # Support both nested list structures (tool_calls[0]) and flat lists
        calls_to_process = []
        if isinstance(tool_calls, list):
            if len(tool_calls) > 0 and isinstance(tool_calls[0], list):
                calls_to_process = tool_calls[0]
            else:
                calls_to_process = tool_calls
        else:
            calls_to_process = [tool_calls]

        messages = []
        for tool_call in calls_to_process:
            if isinstance(tool_call, dict):
                id = tool_call.get('id')
                function_name = tool_call.get('function', dict()).get('name')
                function_arguments = tool_call.get('function', dict()).get('arguments', '{}') 
            else:
                id = tool_call.id
                function_name = tool_call.function.name
                function_arguments = tool_call.function.arguments 
            
            try:
                args = json.loads(function_arguments)
            except Exception:
                args = {}

            # print(f'Tool Call:{function_name}({function_arguments})')
            
            # Dynamic lookup for callable function:
            # 1. Check self.tool_functions
            # 2. Check module globals
            # 3. Check dynamic imports from standard helper modules (e.g. tests.tools)
            func = self.tool_functions.get(function_name) or globals().get(function_name)
            
            if not func:
                # Attempt to dynamically import from known tools packages
                for module_name in ["tests.tools", "tools"]:
                    try:
                        mod = __import__(module_name, fromlist=[function_name])
                        func = getattr(mod, function_name, None)
                        if func:
                            break
                    except ImportError:
                        continue
            
            if func and callable(func):
                try:
                    result = func(**args)
                except Exception as e:
                    result = f"Error executing tool '{function_name}': {str(e)}"
            else:
                result = f"Invalid Tool Call: Function '{function_name}' is not registered or imported."
            # print(f'Result: {result}')

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

    def chat(self, message: str):
        self.chat_history.append({'role': 'user', 'content': message})
        # print(f'You: {message}', flush=True)
        while True:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.chat_history,
                tools=self.tools,
                reasoning_effort=None,
                # reasoning_effort='low',
                # wiki_grounding=True,
                # max_tokens=200,
            )
            # print(response)
            message = response.choices[0].message
            tool_messages =  self.handle_tool_calls(message)
            if not tool_messages:
                break
            self.chat_history += tool_messages
        # print(f'AI Assistant: {message.content}', flush=True)
        self.chat_history.append({'role': 'assistant', 'content': message.content})            
        return message.content

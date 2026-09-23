from sarvamai import SarvamAI
import json
from dotenv import load_dotenv
import os

load_dotenv()
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
client = SarvamAI(
    api_subscription_key=SARVAM_API_KEY,
)

assert SARVAM_API_KEY is not None, "Could NOT load SARVAM_API_KEY from .env"

def get_balance(account_number: str):
    if account_number == '001002':
        return "INR 51203"
    else:
        return "INR 2500"

def get_transactions(account_number: str):
    if account_number == "001002":
        return [
            ("Time", "Transaction", "INR"),
            ("11:21 AM", "Debit - XYZ Super Market", "INR 651.50"),
            ("4:45 PM",  "Credit - Refund from PQR Braodband Services", "INR 999"),
        ]
    else:
        return "No transactions in the last 24 hrs in your account"

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_balance",
            "description": "Get the balance for the account number",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_number": {"type": "string", "description": "Account Number"},
                },
                "required": ["account_number"],
            },
        },
    },
     {
        "type": "function",
        "function": {
            "name": "get_transactions",
            "description": "Get transactions from the last 24 hours",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_number": {"type": "string", "description": "Account Number"},
                },
                "required": ["account_number"],
            },
        },
    },   
]

tools_map  = {
    "get_balance": get_balance,
    "get_transactions": get_transactions,
}

def invoke_tool(f_name: str, f_args: dict):
    return tools_map[f_name](**f_args)


messages=[
    {"role": "system", "content": "You are a Customer Service Rep from ABC Bank."},
]

def chat(user_message: str):    
        
    messages.append(
        {"role": "user", "content": user_message.strip()}
    )

    while True:
        response = client.chat.completions(
            model="sarvam-105b-conversations",
            messages=messages,
            tools=tools,
        )
        if not response.choices[0].message.tool_calls:
            # No tool calls - Let us display the chatbot response to the user
            break
            
        tool_calls = response.choices[0].message.tool_calls
        
        for tool_call in tool_calls:
            f_name = tool_call.function.name #get_balance
            f_args = json.loads(tool_call.function.arguments) # {"account_number": "001002"}
            result = invoke_tool(f_name, f_args)

            messages.append(
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            },
                        }
                    ],
                }
            )
                
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                }
            )             

    assistant_response = response.choices[0].message.content
    messages.append(
        {"role": "assistant", "content": assistant_response}
    )
    return assistant_response
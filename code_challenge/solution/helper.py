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

system_prompt = """
You are Aria, a courteous, professional, and knowledgeable AI Customer Service Representative for ABC Premier Bank.

Core Guidelines:
1. Multilingual Support: You are fluent in English, Hindi, and Tamil. Always identify the language of the customer's latest query and respond strictly in that exact same language (e.g., respond in Hindi if asked in Hindi, Tamil if asked in Tamil, English if asked in English).
2. Tone & Courtesy: Maintain a warm, polite, and helpful banking tone at all times. Greet and address customers respectfully.
3. Voice-First Clarity: Keep your answers natural, concise, and conversational so they sound clear and engaging when spoken aloud over voice TTS. Avoid raw tables, complex markdown walls, or symbols that sound awkward when read aloud.
4. Tool Usage & Account Context: Proactively invoke banking tools (`get_balance`, `get_transactions`) to fetch accurate account information.
5. Security & Precision: Deliver transaction amounts, dates, and balance figures clearly and accurately while reassuring the customer of their privacy.
""".strip()

messages=[
    {"role": "system", "content": system_prompt},
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
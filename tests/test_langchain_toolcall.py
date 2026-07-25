import os

from dotenv import load_dotenv
from langchain_sarvam import ChatSarvam
from langchain.agents import create_agent
from langchain_core.tools import tool

load_dotenv()

if not os.getenv("SARVAM_API_KEY"):
    raise RuntimeError("Set SARVAM_API_KEY in your environment or .env file before running.")

@tool
def get_account_balance(account_number: str):
    """
    Get latest balance for the given account number.
    IMPORTANT: Use the exact account number provided by the user. Do not modify or guess the account number.
    """

    print(f'Invoking: get_account_balance({account_number})\n')

    if account_number == 'ABCD1234':
        return 'Rs. 5000.50'
    elif account_number == '123456789':
        return 'Rs. 12,000'
    elif account_number.startswith('0'):
        return 'INR 1 Lakh'
    else:
        return 'Invalid Account - Please try again'


llm = ChatSarvam(model="sarvam-30b")
# llm_with_tools = llm.bind_tools([get_account_balance])
agent = create_agent(
    model=llm,
    tools=[get_account_balance],
    system_prompt="You are a helpful assistant that can answer questions about bank accounts. When using tools, always pass the EXACT parameter values from the user's query. Never modify, guess, or substitute values.",
)

def test_tool_calling(text: str):
    try:
        message = {'role': 'user', 'content': text}
        print(f'Invoking agent with: {message}\n')
        result = agent.invoke(message)
        print(f'Agent response: {result['messages'][-1].content}\n')
        print(f'Full result: {result}')
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_tool_calling('what is the balance for account ABCD1234 ?')

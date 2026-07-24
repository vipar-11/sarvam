import os

from dotenv import load_dotenv
from langchain_sarvam import ChatSarvam
from langchain_core.tools import tool
from tests.tools import get_account_balance as get_account_balance_tool
from pydantic import BaseModel

load_dotenv()

if not os.getenv("SARVAM_API_KEY"):
    raise RuntimeError("Set SARVAM_API_KEY in your environment or .env file before running.")

@tool
def get_account_balance(account_number: str):
    """Get the current balance of a bank account"""
    print('Tool invoked')
    return get_account_balance_tool(account_number)

class CapitalCity(BaseModel):
    city: str
    country: str

class CityInfo(BaseModel):
    city: str
    native_language: str
    local_greeting: str

llm = ChatSarvam(model="sarvam-30b")
llm_with_tools = llm.bind_tools([get_account_balance])
structured_llm = llm.with_structured_output(CapitalCity)
structured_llm2 = llm.with_structured_output(CityInfo)
   

def test_invoke(text : str):
    try:
        response = llm.invoke(text)
        print(response.content) 
    except Exception as e:
        print(f"Error: {e}")

def test_stream(text : str):
    try:
        for chunk in llm.stream(text):
            print(chunk.content, end="", flush=True)
    except Exception as e:
        print(f"Error: {e}")

def test_tool_calling(text: str):
    try:
        response = llm_with_tools.invoke(text)
        print(response.tool_calls) 
        print(response.content) 
    except Exception as e:
        print(f"Error: {e}")

def test_structured_output(text: str):
    try:
        response = structured_llm.invoke(text)
        print(response) 
    except Exception as e:
        print(f"Error: {e}")

def test_structured_output2(text: str):
    try:
        response = structured_llm2.invoke(text)
        print(response) 
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    # test_invoke('Hi, How are you ?')
    # test_stream('Hi, How are you ?')
    test_tool_calling('what is the balnance for account abcd1234?')
    # test_structured_output("What is the capital of France?")
    # test_structured_output2("Can you tell me about the native language spoken in chennai along with a local greeting in the local script ?")

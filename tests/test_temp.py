import os

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_sarvam import ChatSarvam

load_dotenv()

if not os.getenv("SARVAM_API_KEY"):
    raise RuntimeError("Set SARVAM_API_KEY in your environment or .env file before running.")


@tool
def get_weather(city: str) -> str:
    """Get the weather for a city."""
    return f"Sunny in {city}"


llm = ChatSarvam(model="sarvam-105b")
llm_with_tools = llm.bind_tools([get_weather])

try:
    response = llm_with_tools.invoke("What is the weather in Mumbai?")
    print(response)
except Exception as e:
    print(f"Error: {e}")

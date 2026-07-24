from openai import OpenAI
from dotenv import load_dotenv
import os

from pydantic import BaseModel, Field
from typing import List

class CityInfo(BaseModel):
    city: str = Field(description="City name")
    local_language: str = Field(description="Language spoken in the city")
    short_greeting_in_local_language: str = Field(description="Greeting in the local language")

load_dotenv()

# Initialize OpenAI client pointed at Sarvam AI
client = OpenAI(
    api_key=os.getenv("SARVAM_API_KEY"),
    base_url="https://api.sarvam.ai/v1"
)

def test_llm_call():
    response = client.chat.completions.create(
        model="sarvam-30b",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "How are you ?"}
        ]
    )
    print(response.choices[0].message.content)

def test_structured_ouputs():
    response = client.beta.chat.completions.parse(
        model="sarvam-30b", 
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Give me the requested information on Chennai"}
        ],
        response_format=CityInfo,
    )
    structured_output = response.choices[0].message.parsed
    print(structured_output.city)
    print(structured_output.local_language)
    print(structured_output.short_greeting_in_local_language)
    
    

if __name__ == '__main__':
    # test_llm_call()
    test_structured_ouputs()


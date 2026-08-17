import openai
import os
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

response = client.responses.create(
    # model="llama-3.3-70b-versatile",
    # model='groq/compound',
    model="openai/gpt-oss-120b",
    input="give me a nice question on probability that I can test knowledge of students in. Give me only the question and not the answer.",
)

print(response.output_text)


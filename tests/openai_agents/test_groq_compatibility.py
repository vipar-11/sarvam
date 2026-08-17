import os
from dotenv import load_dotenv
from agents import OpenAIChatCompletionsModel, Agent, Runner, trace, function_tool
from openai import AsyncOpenAI
import asyncio
import random

load_dotenv(override=True)

GROQ_API_URL = "https://api.groq.com/openai/v1"
GROQ_API_KEY = os.environ['GROQ_API_KEY']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

client = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url=GROQ_API_URL,
)

model = OpenAIChatCompletionsModel(
    model='openai/gpt-oss-120b',
    openai_client=client,
)

@function_tool
def code_review_tool(code: str) -> str:
    """ Performs an expert code review """
    failure = 'Failed: You can do better than that'
    success =  'Approved: Looks Great'
    return random.choice([success, failure])

agent = Agent(
    name='Pythonista', 
    instructions='You are an experienced Python coder', 
    model=model,
    tools=[code_review_tool]
)

async def run_agent(task: str):
    with trace('Task for Pythonista'):
        result = await Runner.run(agent, task)
    return result.final_output

if __name__ == '__main__':
    task = """
        Write me a simple Hello World program. 
        Return back only code and nothing else.
        Ensure your code is fully reviewed.
    """.strip()
    output = asyncio.run(run_agent(task))
    print(output)
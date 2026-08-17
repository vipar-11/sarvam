import os
from dotenv import load_dotenv
from agents import OpenAIChatCompletionsModel, Agent, Runner, trace, function_tool
from openai import AsyncOpenAI
import asyncio
import random
from rich.console import Console
console = Console()

load_dotenv(override=True)

GROQ_API_URL = "https://api.groq.com/openai/v1"
GROQ_API_KEY = os.environ['GROQ_API_KEY']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
DEEPSEEK_API_URL = 'https://api.deepseek.com'

checklist = []
status = []

client = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url=GROQ_API_URL,
)

# client2 = AsyncOpenAI(
#     api_key=os.environ['DEEPSEEK_API_KEY'],
#     base_url=DEEPSEEK_API_URL,

# )

model = OpenAIChatCompletionsModel(
    model='openai/gpt-oss-120b',
    openai_client=client,
)

# model = OpenAIChatCompletionsModel(
#     model='deepseek-v4-flash',
#     openai_client=client2,
# )

def format_item(idx: int, item: str, status: bool) -> str:
    return f'[green][strike]{idx}. {item}[/strike] - Completed[/green]' if status else f'[red]{idx}. {item} - Pending[/red]'

def get_checklist():
    global checklist, status
    # print('get_checklist()')
    checklist_formatted = []
    for idx, (item, status_) in enumerate(zip(checklist, status)):
        line = f'{format_item(idx+1, item, status_)}'
        checklist_formatted.append(line)
    checklist_formatted = '\n'.join(checklist_formatted) + '\n'
    console.print(checklist_formatted)
    return checklist_formatted

@function_tool
def create_checklist(items: list[str]) -> str:
    """ Creates a checklist of Items and returns the latest status """
    # print('create_checklist()')
    global checklist, status
    checklist += items
    status += [False] * len(items)
    return get_checklist()

@function_tool
def mark_complete(item_id: int, completion_notes: str) -> str   :
    """ Marks a checklist item as completed and returns the latest status """
    # print('mark_commplete()')
    global checklist
    console.print(f'\n[blue]{completion_notes}[/blue]\n')
    status[item_id - 1] = True
    return get_checklist()


agent = Agent(
    name='Pythonista', 
    instructions="""
        You are a helpful problem solver.
        Solve the problem you are given. 
        Plan your work using the checklist and execute on your tasks.
        You must make use of the tools.
    """, 
    model=model,
    tools=[create_checklist, mark_complete]
)

async def run_agent(task: str):
    with trace('Task for Planning Agent'):
        result = await Runner.run(agent, task)
    return result.final_output

if __name__ == '__main__':
    task = """
    Code a simple chatbot - front end, middletier and backend.
    """.strip()
    output = asyncio.run(run_agent(task))
    print(output)
    # create_checklist(['hello', 'world'])
    # mark_complete(1, 'completed')
    # mark_complete(2, 'completed')

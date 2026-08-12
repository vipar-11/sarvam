
import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

f_desc = lambda is_complete: 'Completed' if is_complete else 'Pending'

class Checklist:
    def __init__(self):
        self.items = []
        self.status = []

    def get_checklist(self):
        checklist = []
        for item_id, (item, status) in enumerate(zip(self.items, self.status), start=1):
            checklist_item = f'{item_id}. {item} {f_desc(status)}'
            checklist.append(checklist_item)
        checklist_formatted = '\n'.join(checklist)
        print(checklist_formatted, '\n')
        return checklist_formatted

    def add(self, items: list[str]):
        self.items.extend(items)
        self.status.extend([False]*len(items))
        return self.get_checklist()

    def mark_complete(self, item_id: int, completion_notes: str="executed"):
        self.status[item_id-1] = True
        print(completion_notes, '\n')
        return self.get_checklist()
    
checklist = Checklist()
add_items_to_checklist = lambda items: checklist.add(items)
mark_item_as_complete = lambda item_id, completion_notes: checklist.mark_complete(item_id, completion_notes)


agent_tools = [
    {
        "type": "function",
        "function": {
            "name": "add_items_to_checklist",
            "description": "Add items to checklist",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": ["items"],
                "additionalProperties": False,
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mark_item_as_complete",
            "description": "Mark item as complete",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_id": {
                        "type": "integer"
                    },
                    "completion_notes": {
                        "type": "string"
                    }
                },
                "required": ["item_id", "completion_notes"],
                "additionalProperties": False,
            },
        }
    }
]

agent_tools_map = {
    "add_items_to_checklist": add_items_to_checklist,
    "mark_item_as_complete": mark_item_as_complete
}

def handle_tool_calls(tool_calls: list):
    messages = []
    for tool_call in tool_calls:
        tool_call_id = tool_call.id
        tool_name = tool_call.function.name
        tool_args = tool_call.function.arguments
        f = agent_tools_map.get(tool_name)
        args = json.loads(tool_args)
        # print(tool_name, tool_args)
        result = f(**args) if f else 'Tool Not Found'
        messages.append(
            {
                'role': 'tool',
                'tool_call_id': tool_call_id,
                'content': json.dumps(result)
            }
        )
    return messages


class Agent:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt

    def execute(self, instructions: str):
        messages=[
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": instructions}
        ]

        while True:
            # print(messages)
            response = client.chat.completions.create(
                model='openai/gpt-oss-120b',
                messages=messages,
                tools=agent_tools,
            )
            # print()
            # print(response)

            if response.choices[0].finish_reason != 'tool_calls':
                break
            tool_calls = response.choices[0].message.tool_calls
            messages.append(response.choices[0].message)
            messages += handle_tool_calls(tool_calls)

        return response.choices[0].message.content

if __name__ == '__main__':
#     system_prompt = """
# You are given a problem to solve, by using your checklist tools to plan a list of steps, then carrying out each step in turn.
# Now create a plan, set the checklist, carry out the steps, and reply with the solution.
# If any quantity isn't provided in the question, then include a step to come up with a reasonable estimate.
# Provide your solution in Rich console markup without code blocks.
# Do not ask the user questions or clarification; respond only with the answer after using your tools.
#     """.strip()
    system_prompt = """
    You are a helpful problem solver.
    Solve the problem you are given. Plan your work using the checklist and execute on your tasks.
    """
    agent = Agent(system_prompt)

    instructions = """
    plan my calendar for tomorrow.
    I have the following activities:
    Perform Sandhyavandanam 3 times
    Attend Veda Class
    Do Course on Udemy on Agentic AI by Ed Donner
    Take the session on EPFO for Dilan
    Teach Vishal after he return from school
    Do some personal Financial Planning 
    """.strip()
    response = agent.execute(instructions)
    print(response)
    
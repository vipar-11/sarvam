from sarvamai import SarvamAI
from dotenv import load_dotenv
import base64
import io
import os
import sounddevice as sd
import soundfile as sf

from tests.test_echo_speech import record_to_memory
from tests.tools import tools, handle_tool_calls

load_dotenv()

API_KEY = os.getenv("SARVAM_API_KEY")
MODEL = 'sarvam-30b'


class ChatBot:

    def __init__(self, api_key: str, model: str, speech: bool=False, system_prompt: str=None, tools: list=None):
        self.client = SarvamAI(api_subscription_key=api_key)
        self.model = model        
        self.speech = speech
        self.tools = tools
        self.chat_history = [{'role': 'system', 'content': system_prompt}] if system_prompt else []

    def text_to_speech(self, text: str):
        audio = self.client.text_to_speech.convert(
            text=text,
            model="bulbul:v3",
            target_language_code="ta-IN",
            speaker="ishita",            
        )

        combined_audio = "".join(audio.audios)
        audio_bytes = base64.b64decode(combined_audio)

        data, samplerate = sf.read(io.BytesIO(audio_bytes))
        sd.play(data, samplerate)
        sd.wait()

    def speech_to_text(self, wav_data: bytes):
        response = self.client.speech_to_text.transcribe(
            file=io.BytesIO(wav_data),
            model="saaras:v3",
            mode="transcribe"  # or "translate", "verbatim", "translit", "codemix"
        )
        return response.transcript

    def chat(self, message: str):
        self.chat_history.append({'role': 'user', 'content': message})
        while True:
            response = self.client.chat.completions(
                model=self.model,
                messages=self.chat_history,
                tools=self.tools,
                reasoning_effort='low',
                # wiki_grounding=True,
                max_tokens=200,
            )
            # print(response)
            message = response.choices[0].message
            tool_messages =  handle_tool_calls(message)
            if not tool_messages:
                break
            self.chat_history += tool_messages

        self.chat_history.append({'role': 'assistant', 'content': message.content})
        if self.speech:
            self.text_to_speech(message.content)
            
        return message.content

    def handle_stream(self, stream: any):
        tool_call_id = ''
        function_name = ''
        function_arguments = ''
        content_buffer = ''
        has_tool_call = False
        for chunk in stream:
            # print(chunk, '\n', flush=True)
            if not chunk.choices:
                continue
            if chunk.choices[0].delta.content:
                if not chunk.choices[0].delta.content.isspace() and not has_tool_call:
                    yield content_buffer + chunk.choices[0].delta.content
                    content_buffer = ''
                else:
                    content_buffer += chunk.choices[0].delta.content
            if chunk.choices[0].delta.tool_calls:
                has_tool_call = True
                tool_call = chunk.choices[0].delta.tool_calls[0]
                tool_call_id += tool_call.id if tool_call.id else ''
                function = tool_call.function
                function_name += function.name if function.name else ''
                function_arguments += function.arguments if function.arguments else ''
        
        if has_tool_call:
            # print('function_name', function_name)
            # print('function_arguments', function_arguments)
            return {
                'tool_calls' : [
                    {
                        'id': tool_call_id,
                        'function': {
                            'name': function_name,
                            'arguments': function_arguments,
                        }
                    }
                ]
            }

    def chat_stream(self, message: str):
        self.chat_history.append({'role': 'user', 'content': message})
        response_parts = []

        while True:
            stream = self.client.chat.completions(
                model=self.model,
                messages=self.chat_history,
                tools=self.tools,
                stream=True,
                reasoning_effort='low',
                # wiki_grounding=True,
                max_tokens=200,
            )
            # print(self.chat_history)
            gen = self.handle_stream(stream)    
            try:
                while True:
                    response_part = next(gen)
                    response_parts.append(response_part)
                    yield response_part
            except StopIteration as e:
                if e.value:
                    # print('exception generated', e.value)
                    tool_messages =  handle_tool_calls(e.value)
                    self.chat_history += tool_messages
                    continue
            break
            
        response_full = ''.join(response_parts)
        if self.speech:
            self.text_to_speech(response_full)

        self.chat_history.append({'role': 'assistant', 'content': response_full})


def test_chat():
    bot = ChatBot(API_KEY, MODEL)
    while True:
        user_input = input("\nYou: ")
        print("Bot:", bot.chat(user_input), "\n")

def test_chat_stream(speech: bool=False, tools: list=None):
    bot = ChatBot(API_KEY, MODEL, speech=speech, tools=tools)
    while True:
        user_input = input("\nYou: ")
        print("\nBot: ", end="")
        for part in bot.chat_stream(user_input):
            print(part, end="", flush=True)
        print("\n")

def test_voice_bot():
    bot = ChatBot(API_KEY, MODEL, speech=True)
    while True:
        wav_data, _ = record_to_memory()
        text = bot.speech_to_text(wav_data)
        bot.chat(text)

def test_banking_agents_with_tools():
    global tools
    system_prompt = """
    You are a honest, professional and helpful banking assistant providing clear and crisp single line responses.
    Use the available tools to answer user queries in a natural conversational tone.
    Your responses will be converted into a voice message.
    """
    # bot = ChatBot(API_KEY, MODEL, system_prompt=system_prompt, tools=tools)
    # while True:
    #     user_input = input("\nYou: ")
    #     print("Bot:", bot.chat(user_input), "\n")

    bot = ChatBot(API_KEY, MODEL, speech=True, system_prompt=system_prompt, tools=tools)
    while True:
        wav_data, _ = record_to_memory()
        text = bot.speech_to_text(wav_data)
        bot.chat(text)
        


if __name__ == "__main__":
    # test_chat()
    # test_chat_stream()
    # test_chat_stream(speech=True)
    # test_chat_stream(tools=tools)
    # test_voice_bot()
    test_banking_agents_with_tools()

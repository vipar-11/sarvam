from placement_cell import chatbot
import os
from dotenv import load_dotenv

from placement_cell.chatbot import ChatBot
from placement_cell.main import (
    get_upcoming_companies, 
    check_eligibility_and_apply, 
    set_interview_reminder,
    placement_tools
)

load_dotenv()
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

def init_bot():
    bot = ChatBot(
        api_key=DEEPSEEK_API_KEY,
        model="deepseek-v4-pro",
        system_prompt=(
            "You are a warm, helpful campus placement coordinator at Agni College of Technology. "
            # "Greet the student. Briefly present the upcoming IT companies (Google, Microsoft, Infosys). "
            # "Ask if they want to apply to any company. Use the check_eligibility_and_apply tool to "
            # "perform qualifications checking and submit their application. "
            # "Once applied, ask if they want to do a technical mock interview. "
            # "If they agree, ask them exactly 3 technical or behavioral questions one by one. "
            # "Evaluate/acknowledge their replies briefly, then move to the next question. "
            # "At closure, ask if they want a reminder scheduled before their interview slot. "
            "Keep your responses friendly, concise (1-2 sentences max), and conversational."
            "Your responses will be converted into a human voice - so make sure you respond appropriately"
        ),
        tools=placement_tools
    )
    bot.register_tool("get_upcoming_companies", get_upcoming_companies)
    bot.register_tool("check_eligibility_and_apply", check_eligibility_and_apply)
    bot.register_tool("set_interview_reminder", set_interview_reminder)
    return bot

def test_chat():
    bot = init_bot()
    while True:
        user_input = input("\nYou: ")
        print("Bot:", bot.chat(user_input), "\n")

if __name__ == "__main__":
    test_chat()
from sarvamai import SarvamAI
from dotenv import load_dotenv
import os

load_dotenv()

client = SarvamAI(
    api_subscription_key=os.getenv("SARVAM_API_KEY")
)

def translate(text: str, source: str = "en-IN", target: str = "hi-IN", gender: str = "Male"):
    response = client.text.translate(
        input=text,
        source_language_code=source,
        target_language_code=target,
        speaker_gender=gender
    )
    return response.translated_text

if __name__ == "__main__":
    print(translate(text="My name is Jayaram"))
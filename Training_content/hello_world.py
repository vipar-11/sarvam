from sarvamai import SarvamAI
from dotenv import load_dotenv

SARVAM_API_KEY = load_dotenv()

client = SarvamAI(
    api_subscription_key=SARVAM_API_KEY,
)

response = client.chat.completions(
    model="sarvam-105b",
    messages=[
        {"role": "user", "content": "Hey, what is the capital of India?"}
    ],
)
print(response)
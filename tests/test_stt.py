import asyncio
import base64
from sarvamai import AsyncSarvamAI

# Load your audio file
with open("path/to/your/audio.wav", "rb") as f:
    audio_data = base64.b64encode(f.read()).decode("utf-8")

async def basic_transcription():
    # Initialize client with your API key
    client = AsyncSarvamAI(api_subscription_key="YOUR_SARVAM_API_KEY")

    # Connect and transcribe — change mode as needed
    async with client.speech_to_text_streaming.connect(
        model="saaras:v3",
        mode="transcribe",
        language_code="en-IN",
        high_vad_sensitivity=True
    ) as ws:
        await ws.transcribe(audio=audio_data)
        response = await ws.recv()
        print(f"Result: {response}")

asyncio.run(basic_transcription())

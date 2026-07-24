import io
import wave
import sys
import numpy as np
import sounddevice as sd
import soundfile as sf
from sarvamai import SarvamAI
from dotenv import load_dotenv
import os

def record_to_memory(sample_rate: int = 44100, channels: int = 1) -> tuple[bytes, np.ndarray]:
    """
    Records audio into memory until the user presses ENTER.
    Returns:
        wav_bytes: Complete WAV file contents in RAM (bytes).
        audio_data: Raw NumPy array of 16-bit audio samples.
    """
    audio_frames = []

    def callback(indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        # Store a copy of incoming raw bytes in RAM
        audio_frames.append(indata.copy())

    print("🎙️ Recording to RAM... Press ENTER to stop.")
    
    # Non-blocking audio input stream
    with sd.InputStream(samplerate=sample_rate, channels=channels, dtype='int16', callback=callback):
        input()  # Wait for user keypress

    print("⏹️ Stopped recording. Encoding to memory buffer...")

    # Combine array chunks into a single NumPy array
    raw_array = np.concatenate(audio_frames, axis=0)

    # Write WAV structure to an in-memory BytesIO buffer
    memory_buffer = io.BytesIO()
    with wave.open(memory_buffer, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16-bit audio = 2 bytes per sample
        wf.setframerate(sample_rate)
        wf.writeframes(raw_array.tobytes())

    # Extract the complete raw bytes from the buffer
    wav_bytes = memory_buffer.getvalue()
    
    return wav_bytes, raw_array

# Example Usage
if __name__ == "__main__":
    wav_data, audio_np = record_to_memory()
    
    # 1. Inspect buffer size in RAM
    buffer_size_mb = len(wav_data) / (1024 * 1024)
    print(f"\n📊 In-Memory Stats:")
    print(f" - Buffer size: {buffer_size_mb:.2f} MB")
    print(f" - Sample shape: {audio_np.shape}")
    print(f" - Duration: {len(audio_np) / 44100:.2f} seconds")

    data, samplerate = sf.read(io.BytesIO(wav_data))
    sd.play(data, samplerate)
    sd.wait()

    load_dotenv()
    API_KEY = os.getenv("SARVAM_API_KEY")

    client = SarvamAI(api_subscription_key=API_KEY)
    response = client.speech_to_text.transcribe(
        file=io.BytesIO(wav_data),
        model="saaras:v3",
        mode="transcribe"  # or "translate", "verbatim", "translit", "codemix"
    )
    print(response.transcript)

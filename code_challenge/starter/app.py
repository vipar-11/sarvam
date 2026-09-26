import os
import tempfile
import gradio as gr

# =====================================================================
# Placeholder functions for STT, Chatbot, and TTS
# (Replace these with your actual API calls when ready)
# =====================================================================

def speech_to_text(audio_filepath: str) -> str:
    """
    Placeholder for Speech-to-Text (STT) conversion.
    
    Args:
        audio_filepath: Path to the recorded audio file from the microphone.
        
    Returns:
        Transcribed text string.
    """
    if not audio_filepath or not os.path.exists(audio_filepath):        
        return ""
    # TODO: Replace with actual STT API call (e.g. Sarvam Saaras / Whisper)
    return "Hello! This is a mock transcription of your voice recording."


def get_chatbot_response(user_text: str, conversation_history: list) -> str:
    """
    Placeholder for LLM / Chatbot response generation.
    
    Args:
        user_text: Transcribed user message.
        conversation_history: Prior conversation messages list.
        
    Returns:
        Assistant response text string.
    """
    # TODO: Replace with actual Chatbot / LLM API call
    return f"Hi, I received your message."


def text_to_speech(text_response: str, fallback_audio_filepath: str = None) -> str:
    """
    Placeholder for Text-to-Speech (TTS) conversion.
    For this prototype, it returns the user's recorded audio file to play back.
    
    Args:
        text_response: The assistant's text response to synthesize.
        fallback_audio_filepath: Path to the recorded audio to play back.
        
    Returns:
        Path to the output audio file.
    """
    # TODO: Replace with actual TTS API call (e.g. Sarvam Bulbul / ElevenLabs)
    # print("text_response from TTS", text_response)
    
    return fallback_audio_filepath


# =====================================================================
# Main Audio Processing Pipeline
# =====================================================================

def process_audio(audio_filepath: str, conversation_history: list):
    """
    Processes the recorded audio file:
    1. Transcribes audio to text (STT)
    2. Sends text to chatbot for response
    3. Converts assistant response to audio (TTS)
    4. Appends turn to conversation history.
    5. Returns (updated_history, assistant_audio, None) so mic_input automatically resets to Record state.
    """
    if conversation_history is None:
        conversation_history = []

    if not audio_filepath:
        return conversation_history, None, None

    # Step 1: Speech to Text (STT)
    user_text = speech_to_text(audio_filepath)
    if not user_text:
        return conversation_history, None, None

    # Step 2: Chatbot response
    assistant_text = get_chatbot_response(user_text, conversation_history)

    # Step 3: Text to Speech (TTS)
    assistant_audio = text_to_speech(assistant_text, fallback_audio_filepath=audio_filepath)

    # Step 4: Update conversation history
    updated_history = list(conversation_history)
    updated_history.append({"role": "user", "content": user_text})
    updated_history.append({"role": "assistant", "content": assistant_text})

    # Returning None for mic_input immediately resets the recorder so 'Record' is ready for next turn
    return updated_history, assistant_audio, None


# =====================================================================
# Client-side Voice Activity Detection (VAD) JavaScript
# Automatically stops the recording when a pause is detected
# =====================================================================

VAD_JAVASCRIPT = """
() => {
    let audioContext = null;
    let analyser = null;
    let microphone = null;
    let isSpeaking = false;
    let silenceStartTime = 0;
    let vadInterval = null;
    let activeStream = null;

    // Detection settings
    const SILENCE_THRESHOLD = 14;   // RMS / volume sensitivity threshold (0-255)
    const PAUSE_DURATION_MS = 1200; // 1.2s silence after speech triggers stop

    function updateStatus(text, color) {
        const badge = document.getElementById("vad_status_badge");
        if (badge) {
            badge.innerText = text;
            if (color) badge.style.color = color;
        }
    }

    function triggerStopRecording() {
        const micContainer = document.getElementById("user_mic");
        if (!micContainer) return;

        // Find the recording stop button inside the Gradio Audio component
        const buttons = micContainer.querySelectorAll("button");
        for (const btn of buttons) {
            const aria = (btn.getAttribute("aria-label") || "").toLowerCase();
            const title = (btn.getAttribute("title") || "").toLowerCase();
            const text = (btn.innerText || "").toLowerCase();
            
            // Check for stop button
            if (
                aria.includes("stop") ||
                title.includes("stop") ||
                text.includes("stop") ||
                btn.classList.contains("stop")
            ) {
                btn.click();
                return;
            }
        }
        
        // Fallback: If recording is active, clicking the main icon/button stops recording
        if (buttons.length > 0) {
            buttons[0].click();
        }
    }

    function stopVAD() {
        if (vadInterval) {
            clearInterval(vadInterval);
            vadInterval = null;
        }
        isSpeaking = false;
        silenceStartTime = 0;
        activeStream = null;
        if (audioContext && audioContext.state !== "closed") {
            audioContext.close().catch(() => {});
            audioContext = null;
        }
        updateStatus("⚪ Idle. Click Record when ready to talk.", "#6b7280");
    }

    function startVAD(stream) {
        stopVAD();
        activeStream = stream;
        updateStatus("👂 Listening... Speak into the microphone.", "#3b82f6");

        try {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioContext.createAnalyser();
            analyser.fftSize = 512;
            analyser.smoothingTimeConstant = 0.2;

            microphone = audioContext.createMediaStreamSource(stream);
            microphone.connect(analyser);

            const dataArray = new Uint8Array(analyser.frequencyBinCount);

            vadInterval = setInterval(() => {
                if (!activeStream || !analyser) return;

                analyser.getByteFrequencyData(dataArray);
                let sum = 0;
                for (let i = 0; i < dataArray.length; i++) {
                    sum += dataArray[i];
                }
                const volume = sum / dataArray.length;
                const now = Date.now();

                if (volume > SILENCE_THRESHOLD) {
                    if (!isSpeaking) {
                        isSpeaking = true;
                        updateStatus("🎙️ Speaking detected... Listening...", "#10b981");
                    }
                    silenceStartTime = 0;
                } else if (isSpeaking) {
                    if (silenceStartTime === 0) {
                        silenceStartTime = now;
                    } else {
                        const elapsed = now - silenceStartTime;
                        if (elapsed >= PAUSE_DURATION_MS) {
                            // Pause detected! Stop recording
                            updateStatus("✅ Pause detected! Processing response...", "#f59e0b");
                            stopVAD();
                            triggerStopRecording();
                        } else {
                            updateStatus(`⏳ Pause detected (${(elapsed/1000).toFixed(1)}s)...`, "#f59e0b");
                        }
                    }
                }
            }, 80);
        } catch (err) {
            console.error("VAD initialization failed:", err);
        }
    }

    // Intercept mediaDevices.getUserMedia so VAD starts whenever the user clicks Record
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const originalGetUserMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
        navigator.mediaDevices.getUserMedia = async function(constraints) {
            const stream = await originalGetUserMedia(constraints);
            if (constraints && (constraints.audio || constraints === true)) {
                startVAD(stream);
                stream.getAudioTracks().forEach(track => {
                    track.addEventListener("ended", () => stopVAD());
                });
            }
            return stream;
        };
    }
}
"""

# =====================================================================
# Gradio UI Setup (Optimized Screen-Fit Layout)
# =====================================================================

def create_ui():
    with gr.Blocks(title="Voice Chatbot") as demo:
        gr.Markdown(
            """
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h2 style="margin: 0; font-size: 20px;">🎙️ Voice-to-Voice AI Assistant</h2>
                <div style="font-size: 13px; font-weight: 500;">
                    Status: <span id="vad_status_badge" style="color: #6b7280;">⚪ Idle. Click Record to talk.</span>
                </div>
            </div>
            """
        )

        with gr.Row(equal_height=True):
            # Left Column: User Voice Input & Instructions
            with gr.Column(scale=4, min_width=320):
                gr.Markdown("### 🎤 Voice Input")
                mic_input = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    elem_id="user_mic",
                    label="Click Record, speak, and pause when done",
                )

                gr.Markdown(
                    """
                    <div style="background: rgba(125, 125, 125, 0.08); border-radius: 8px; padding: 12px; margin-top: 8px; font-size: 13px; line-height: 1.5;">
                        <strong>💡 How to use:</strong><br>
                        1. Click <strong>Record</strong> and speak.<br>
                        2. Pause naturally (~1.2s) — it will <strong>auto-submit</strong>.<br>
                        3. Listen to the assistant and click <strong>Record</strong> for your next turn.
                    </div>
                    """
                )

            # Right Column: Assistant Audio Output (Row 1) & Conversation History (Row 2)
            with gr.Column(scale=6):
                # Row 1: Assistant Voice Output
                with gr.Row():
                    audio_output = gr.Audio(
                        label="🔊 Assistant Voice Response",
                        type="filepath",
                        autoplay=True,
                        interactive=False,
                    )

                # Row 2: Conversation History
                with gr.Row():
                    chatbot_display = gr.Chatbot(
                        label="💬 Conversation History",
                        height=350,
                        buttons=["copy"],
                    )

        # Automatic submit when recording stops (either automatically via pause or manually)
        mic_input.stop_recording(
            fn=process_audio,
            inputs=[mic_input, chatbot_display],
            outputs=[chatbot_display, audio_output, mic_input],
        )

    return demo


if __name__ == "__main__":
    custom_css = """
    .gradio-container {
        max-width: 1100px !important;
        margin: 10px auto !important;
        padding-top: 4px !important;
    }
    #vad_status_badge {
        transition: all 0.2s ease-in-out;
    }
    """
    demo = create_ui()
    demo.launch(theme=gr.themes.Soft(), css=custom_css, js=VAD_JAVASCRIPT, share=False)

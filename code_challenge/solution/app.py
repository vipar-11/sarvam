import os
import tempfile
import gradio as gr

from helper import chat, messages as helper_messages
from sarvamai import SarvamAI
from sarvamai.play import save
from dotenv import load_dotenv

load_dotenv()
SARVAM_API_KEY = os.getenv('SARVAM_API_KEY')
client = SarvamAI(api_subscription_key=SARVAM_API_KEY)


def transcribe_audio_to_text(audio_data: any):
    response = client.speech_to_text.transcribe(
        file=audio_data,
        model="saaras:v3",
        mode="transcribe"
    )
    return response.transcript


def speech_to_text(audio_filepath: str) -> str:
    """Transcribe user audio to text using Sarvam Saaras STT."""
    if not audio_filepath or not os.path.exists(audio_filepath):
        return ""
    return transcribe_audio_to_text(open(audio_filepath, "rb"))


def get_chatbot_response(user_text: str, conversation_history: list) -> str:
    """Generate banking assistant response using Sarvam LLM with tool calling."""
    assistant_text = chat(user_text)
    return assistant_text


def text_to_speech(text_response: str, fallback_audio_filepath: str = None) -> str:
    """Synthesize assistant response into natural voice using Sarvam Bulbul TTS."""
    audio = client.text_to_speech.convert(
        language_code="en-IN",
        text=text_response,
        model="bulbul:v3",
        speaker="shubh",
    )
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        audio_path = tmp_file.name
    save(audio, audio_path)
    return audio_path


def process_audio(audio_filepath: str, conversation_history: list):
    """
    Main voice processing turn:
    1. STT -> 2. Chatbot response with tool calls -> 3. TTS -> 4. Update conversation.
    """
    if conversation_history is None:
        conversation_history = []

    if not audio_filepath:
        return conversation_history, None, None

    # Step 1: STT
    user_text = speech_to_text(audio_filepath)
    if not user_text:
        return conversation_history, None, None

    # Step 2: Chatbot response
    assistant_text = get_chatbot_response(user_text, conversation_history)

    # Step 3: TTS
    assistant_audio = text_to_speech(assistant_text, fallback_audio_filepath=audio_filepath)

    # Step 4: Update conversation history
    updated_history = list(conversation_history)
    updated_history.append({"role": "user", "content": user_text})
    updated_history.append({"role": "assistant", "content": assistant_text})

    return updated_history, assistant_audio, None


def clear_session():
    """Reset the conversation session and voice agent context."""
    global helper_messages
    helper_messages.clear()
    helper_messages.append({"role": "system", "content": "You are a Customer Service Rep from ABC Bank."})
    return [], None, None


# =====================================================================
# Client-side Voice Activity Detection (VAD) & Interactive Soundwave JS
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

    const SILENCE_THRESHOLD = 14;   // RMS threshold
    const PAUSE_DURATION_MS = 1200; // 1.2s silence triggers auto-submit

    function updateStatus(text, badgeClass) {
        const badge = document.getElementById("vad_status_badge");
        const waveBox = document.getElementById("audio_wave_visualizer");
        if (badge) {
            badge.innerText = text;
            badge.className = "status-pill " + (badgeClass || "status-idle");
        }
        if (waveBox) {
            if (badgeClass === "status-speaking") {
                waveBox.classList.add("wave-active");
            } else {
                waveBox.classList.remove("wave-active");
            }
        }
    }

    function triggerStopRecording() {
        const micContainer = document.getElementById("user_mic");
        if (!micContainer) return;

        const buttons = micContainer.querySelectorAll("button");
        for (const btn of buttons) {
            const aria = (btn.getAttribute("aria-label") || "").toLowerCase();
            const title = (btn.getAttribute("title") || "").toLowerCase();
            const text = (btn.innerText || "").toLowerCase();
            
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
        updateStatus("🟢 Ready • Tap Record to speak", "status-idle");
    }

    function startVAD(stream) {
        stopVAD();
        activeStream = stream;
        updateStatus("👂 Listening... Speak now", "status-listening");

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
                        updateStatus("🎙️ Voice Detected • Streaming to Sarvam AI...", "status-speaking");
                    }
                    silenceStartTime = 0;
                } else if (isSpeaking) {
                    if (silenceStartTime === 0) {
                        silenceStartTime = now;
                    } else {
                        const elapsed = now - silenceStartTime;
                        if (elapsed >= PAUSE_DURATION_MS) {
                            updateStatus("⚡ Pause Detected • Processing Banking Response...", "status-processing");
                            stopVAD();
                            triggerStopRecording();
                        } else {
                            updateStatus(`⏳ Silence (${(elapsed/1000).toFixed(1)}s)...`, "status-processing");
                        }
                    }
                }
            }, 80);
        } catch (err) {
            console.error("VAD initialization failed:", err);
        }
    }

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
# Custom Banking Theme CSS
# =====================================================================

BANKING_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

:root {
    --bg-dark: #080c14;
    --surface-dark: #0f172a;
    --surface-card: #131c31;
    --surface-card-border: rgba(255, 255, 255, 0.08);
    --accent-blue: #2563eb;
    --accent-gold: #f59e0b;
    --accent-emerald: #10b981;
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
}

html, body {
    margin: 0 !important;
    padding: 0 !important;
    height: 100vh !important;
    overflow: hidden !important;
    background-color: var(--bg-dark) !important;
}

.gradio-container {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: var(--bg-dark) !important;
    color: var(--text-main) !important;
    max-width: 1400px !important;
    height: 100vh !important;
    max-height: 100vh !important;
    margin: 0 auto !important;
    padding: 8px 16px !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
}

/* Header Bar */
.bank-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid var(--surface-card-border);
    border-radius: 12px;
    padding: 8px 18px;
    margin-bottom: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: nowrap;
}

.bank-logo-group {
    display: flex;
    align-items: center;
    gap: 10px;
}

.bank-logo-icon {
    width: 34px;
    height: 34px;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    box-shadow: 0 2px 10px rgba(37, 99, 235, 0.4);
}

.bank-title {
    font-size: 16px;
    font-weight: 800;
    letter-spacing: -0.3px;
    color: #ffffff;
    margin: 0;
    line-height: 1.1;
}

.bank-subtitle {
    font-size: 9.5px;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: var(--accent-gold);
    font-weight: 700;
    margin: 0;
}

.bank-user-profile {
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(255, 255, 255, 0.04);
    padding: 4px 12px;
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.06);
}

.user-avatar {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: linear-gradient(135deg, #10b981, #059669);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 11px;
    color: white;
}

.user-meta-name {
    font-size: 12px;
    font-weight: 600;
    color: #f1f5f9;
}

.user-meta-sub {
    font-size: 10px;
    color: var(--text-muted);
}

.security-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 10.5px;
    font-weight: 600;
    color: #10b981;
    background: rgba(16, 185, 129, 0.1);
    padding: 3px 8px;
    border-radius: 16px;
    border: 1px solid rgba(16, 185, 129, 0.2);
}

/* Status Badges */
.status-pill {
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    transition: all 0.3s ease;
    white-space: nowrap;
}

.status-idle {
    background: rgba(100, 116, 139, 0.15);
    color: #94a3b8;
    border: 1px solid rgba(148, 163, 184, 0.2);
}

.status-listening {
    background: rgba(37, 99, 235, 0.2);
    color: #60a5fa;
    border: 1px solid rgba(37, 99, 235, 0.4);
    animation: pulseGlow 1.5s infinite;
}

.status-speaking {
    background: rgba(16, 185, 129, 0.2);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.4);
    animation: pulseGlow 1s infinite;
}

.status-processing {
    background: rgba(245, 158, 11, 0.2);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.4);
}

@keyframes pulseGlow {
    0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.4); }
    50% { transform: scale(1.02); box-shadow: 0 0 8px 2px rgba(37, 99, 235, 0.3); }
    100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(37, 99, 235, 0); }
}

/* Integrated Banking & Balance Card */
.bank-card-container {
    background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 60%, #064e3b 100%);
    border-radius: 14px;
    padding: 14px 16px;
    color: white;
    box-shadow: 0 8px 25px -4px rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.12);
    position: relative;
    overflow: hidden;
    margin-bottom: 8px;
}

.bank-card-container::before {
    content: '';
    position: absolute;
    top: -40%;
    right: -25%;
    width: 160px;
    height: 160px;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.2) 0%, transparent 70%);
    border-radius: 50%;
}

.card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.card-chip {
    width: 32px;
    height: 24px;
    background: linear-gradient(135deg, #d97706, #fde047);
    border-radius: 4px;
    box-shadow: inset 0 0 3px rgba(0, 0, 0, 0.3);
}

.card-type {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    color: #e2e8f0;
}

.card-balance-block {
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 10px;
}

.card-balance-label {
    font-size: 9px;
    text-transform: uppercase;
    color: #94a3b8;
    font-weight: 700;
    letter-spacing: 0.8px;
}

.card-balance-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 19px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 2px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 2px;
}

.privacy-pill {
    font-size: 9.5px;
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #60a5fa;
    background: rgba(37, 99, 235, 0.2);
    padding: 2px 6px;
    border-radius: 12px;
    border: 1px solid rgba(37, 99, 235, 0.4);
    letter-spacing: 0;
}

.card-footer {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
}

.card-holder-label {
    font-size: 8px;
    text-transform: uppercase;
    color: #94a3b8;
    letter-spacing: 0.8px;
}

.card-holder-val {
    font-size: 11px;
    font-weight: 700;
    color: #f8fafc;
}

/* Account Controls Widget */
.tx-card {
    background: var(--surface-card);
    border: 1px solid var(--surface-card-border);
    border-radius: 12px;
    padding: 10px 14px;
    margin-bottom: 8px;
}

.tx-header {
    font-size: 11px;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.tx-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.tx-item:last-child {
    border-bottom: none;
    padding-bottom: 0;
}

.tx-icon-group {
    display: flex;
    align-items: center;
    gap: 8px;
}

.tx-icon-circle {
    width: 24px;
    height: 24px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
}

.tx-title { font-size: 11px; font-weight: 600; color: #f1f5f9; }
.tx-time { font-size: 9.5px; color: #64748b; }

/* Prompt Suggestion Chips */
.prompts-container {
    background: var(--surface-card);
    border: 1px solid var(--surface-card-border);
    border-radius: 12px;
    padding: 10px 14px;
}

.prompt-chip {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    padding: 5px 8px;
    margin-bottom: 5px;
    font-size: 10.5px;
    color: #cbd5e1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.prompt-chip:last-child {
    margin-bottom: 0;
}

/* Voice Agent Interface */
.voice-agent-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid var(--surface-card-border);
    border-radius: 12px;
    padding: 8px 14px;
    margin-bottom: 8px;
}

.agent-title-box h3 {
    margin: 0;
    font-size: 15px;
    font-weight: 800;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 6px;
}

.agent-subtitle {
    font-size: 10px;
    color: var(--text-muted);
    margin: 1px 0 0 0;
}

/* Sound Wave */
.wave-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 3px;
    height: 22px;
    padding: 0 4px;
    overflow: visible;
}

.wave-bar {
    width: 2.5px;
    height: 4px;
    background: #3b82f6;
    border-radius: 2px;
    transition: height 0.15s ease;
}

.wave-active .wave-bar {
    animation: waveBounce 0.8s infinite ease-in-out alternate;
}

.wave-active .wave-bar:nth-child(1) { animation-delay: 0.1s; }
.wave-active .wave-bar:nth-child(2) { animation-delay: 0.3s; }
.wave-active .wave-bar:nth-child(3) { animation-delay: 0.2s; }
.wave-active .wave-bar:nth-child(4) { animation-delay: 0.4s; }
.wave-active .wave-bar:nth-child(5) { animation-delay: 0.15s; }

@keyframes waveBounce {
    0% { height: 4px; background: #3b82f6; }
    100% { height: 16px; background: #10b981; }
}

/* Component Labels */
.gradio-container .block-label,
.gradio-container span[data-testid="block-info"],
.gradio-container label span,
.gradio-container .label-wrap {
    color: #f1f5f9 !important;
    font-weight: 700 !important;
    font-size: 11px !important;
    background: transparent !important;
    margin-bottom: 2px !important;
}

/* Zero-Shift Offscreen Autoplay Output */
#assistant_audio,
#assistant_audio * {
    display: none !important;
    position: absolute !important;
    width: 0 !important;
    height: 0 !important;
    max-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
    opacity: 0 !important;
    pointer-events: none !important;
    overflow: hidden !important;
}

#assistant_audio audio {
    display: block !important;
    position: absolute !important;
    width: 0 !important;
    height: 0 !important;
    opacity: 0 !important;
}

/* Fixed Layout Containers - Rigid Zero-Shift Cockpit */
#main_app_row {
    height: calc(100vh - 80px) !important;
    max-height: calc(100vh - 80px) !important;
    overflow: hidden !important;
    gap: 14px !important;
    margin: 0 !important;
}

#left_panel_col {
    height: 100% !important;
    max-height: 100% !important;
    overflow-y: auto !important;
    padding-right: 4px !important;
}

#right_panel_col {
    height: 100% !important;
    max-height: 100% !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 6px !important;
}

/* Voice Agent Header */
.voice-agent-header {
    height: 44px !important;
    min-height: 44px !important;
    max-height: 44px !important;
    flex-shrink: 0 !important;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid var(--surface-card-border);
    border-radius: 12px;
    padding: 6px 14px;
    margin: 0 !important;
    box-sizing: border-box !important;
}

/* Microphone Voice Station - Zero-Shift Locked */
#user_mic, 
#user_mic > div,
#user_mic .gradio-audio {
    height: 48px !important;
    min-height: 48px !important;
    max-height: 48px !important;
    flex-shrink: 0 !important;
    border-radius: 8px !important;
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    box-sizing: border-box !important;
    padding: 0 !important;
    margin: 0 auto !important;
    width: 100% !important;
}

#user_mic .wrapper {
    height: 100% !important;
    max-height: 100% !important;
    background: transparent !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    overflow: hidden !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Single Clean Primary Record Button */
#user_mic .record-button,
#user_mic button.primary,
#user_mic .wrapper > button:first-of-type,
#user_mic button:first-of-type {
    background: linear-gradient(135deg, #1e40af, #2563eb) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    border-radius: 20px !important;
    border: 1px solid rgba(255, 255, 255, 0.25) !important;
    padding: 7px 22px !important;
    box-shadow: 0 2px 12px rgba(37, 99, 235, 0.45) !important;
    cursor: pointer !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    margin: 0 auto !important;
    transition: all 0.2s ease !important;
}

#user_mic .record-button:hover,
#user_mic button.primary:hover {
    transform: scale(1.02) !important;
    box-shadow: 0 4px 16px rgba(37, 99, 235, 0.6) !important;
}

/* Hide all redundant extra stop buttons, toolbar buttons, and hidden controls */
#user_mic button:not(:first-of-type),
#user_mic .toolbar,
#user_mic .secondary-btn,
#user_mic .icon-button:not(.primary),
#user_mic .action-buttons,
#user_mic [aria-label*="clear" i],
#user_mic [aria-label*="delete" i],
#user_mic [aria-label*="download" i],
#user_mic [aria-label*="edit" i],
#user_mic [aria-label*="trim" i],
#user_mic [title*="clear" i],
#user_mic [title*="delete" i] {
    display: none !important;
}

/* Record Dot & Icon - Vivid Luminous Red with Halo */
#user_mic button svg,
#user_mic .record-button svg,
#user_mic [aria-label*="record" i] svg,
#user_mic [title*="record" i] svg {
    filter: drop-shadow(0 0 5px rgba(239, 68, 68, 0.9)) !important;
}

#user_mic button svg circle,
#user_mic button svg path,
#user_mic .record-button svg circle,
#user_mic .record-button svg path,
#user_mic [aria-label*="record" i] svg circle,
#user_mic [aria-label*="record" i] svg path,
#user_mic svg circle,
#user_mic circle,
#user_mic .dot,
#user_mic .record-icon {
    fill: #ff3b30 !important;
    color: #ff3b30 !important;
    stroke: #ffffff !important;
    stroke-width: 1.5px !important;
}

/* Text inside Record button */
#user_mic button span,
#user_mic .record-button span,
#user_mic button div {
    color: #ffffff !important;
    font-weight: 700 !important;
}

/* Chatbot Visibility & Permanent Stationary Sizing */
#chatbot_display,
.gradio-container .chatbot,
.gradio-chatbot {
    background: #0b1120 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.3) !important;
    flex: 1 1 auto !important;
    height: calc(100vh - 215px) !important;
    min-height: 250px !important;
    max-height: calc(100vh - 215px) !important;
    overflow-y: auto !important;
    margin: 0 !important;
    box-sizing: border-box !important;
}

#chatbot_display .wrapper,
#chatbot_display .bubble-wrap,
.gradio-chatbot .wrapper,
.gradio-chatbot .bubble-wrap {
    height: 100% !important;
    overflow-y: auto !important;
}

#chatbot_display .empty,
.gradio-chatbot .empty {
    height: 100% !important;
    min-height: 100% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: #0b1120 !important;
    color: #64748b !important;
}

.gradio-container .user, [data-testid="user"] {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    color: #ffffff !important;
    border-radius: 12px 12px 2px 12px !important;
    border: none !important;
    box-shadow: 0 3px 10px rgba(37, 99, 235, 0.25) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    line-height: 1.4 !important;
    padding: 8px 12px !important;
}

.gradio-container .bot, [data-testid="bot"] {
    background: #1e293b !important;
    color: #f8fafc !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px 12px 12px 2px !important;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    line-height: 1.4 !important;
    padding: 8px 12px !important;
}

.gradio-container .bot p, .gradio-container .bot span, .gradio-container .bot div {
    color: #f8fafc !important;
}

/* Chatbot Custom Scrollbar */
.gradio-container .chatbot *::-webkit-scrollbar {
    width: 5px;
    height: 5px;
}
.gradio-container .chatbot *::-webkit-scrollbar-track {
    background: rgba(15, 23, 42, 0.6);
}
.gradio-container .chatbot *::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 3px;
}

/* Reset Action button & Footer */
#footer_row {
    height: 28px !important;
    min-height: 28px !important;
    max-height: 28px !important;
    flex-shrink: 0 !important;
    margin: 0 !important;
    align-items: center !important;
}

.clear-btn {
    background: rgba(239, 68, 68, 0.1) !important;
    color: #fca5a5 !important;
    border: 1px solid rgba(239, 68, 68, 0.2) !important;
    border-radius: 7px !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    padding: 3px 8px !important;
    height: 26px !important;
    min-height: 26px !important;
    transition: all 0.2s ease !important;
}

.clear-btn:hover {
    background: rgba(239, 68, 68, 0.2) !important;
    border-color: rgba(239, 68, 68, 0.4) !important;
}
"""


def create_ui():
    with gr.Blocks(title="ABC Premier Banking - AI Voice Concierge") as demo:
        # 1. Top Enterprise Banking Navigation Header
        gr.HTML(
            """
            <header class="bank-header">
                <div class="bank-logo-group">
                    <div class="bank-logo-icon">🏛️</div>
                    <div>
                        <h1 class="bank-title">ABC PREMIER BANK</h1>
                        <p class="bank-subtitle">Wealth Management & Digital Voice Concierge</p>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px; flex-wrap: nowrap;">
                    <div class="security-pill">
                        <span>🔒</span> 256-Bit SSL Secured
                    </div>
                    <div class="bank-user-profile">
                        <div class="user-avatar">PB</div>
                        <div>
                            <div class="user-meta-name">Premier Member</div>
                            <div class="user-meta-sub">Diamond Tier • A/C #001002</div>
                        </div>
                    </div>
                </div>
            </header>
            """
        )

        with gr.Row(equal_height=True, elem_id="main_app_row"):
            # Left Column: Banking Overview & Context
            with gr.Column(scale=4, min_width=300, elem_id="left_panel_col"):
                # Metallic Banking Card with Integrated Masked Balance
                gr.HTML(
                    """
                    <div class="bank-card-container">
                        <div class="card-top">
                            <div class="card-chip"></div>
                            <div class="card-type">PREMIER INFINITE •••• 1002</div>
                        </div>
                        <div class="card-balance-block">
                            <div class="card-balance-label">PRIMARY SAVINGS BALANCE</div>
                            <div class="card-balance-val">
                                <span>₹ ••,•••.••</span>
                                <span class="privacy-pill">🔒 Masked</span>
                            </div>
                        </div>
                        <div class="card-footer">
                            <div>
                                <div class="card-holder-label">Cardholder</div>
                                <div class="card-holder-val">PREMIER MEMBER</div>
                            </div>
                            <div style="text-align: right;">
                                <div class="card-holder-label">Expires</div>
                                <div class="card-holder-val">08/29</div>
                            </div>
                            <div style="font-size: 16px; font-weight: 800; font-style: italic; color: #fbbf24;">VISA</div>
                        </div>
                    </div>
                    """
                )

                # Account Controls & Privileges Widget
                gr.HTML(
                    """
                    <div class="tx-card">
                        <div class="tx-header">
                            <span>Account Security & Controls</span>
                            <span style="font-size: 10px; color: #10b981; font-weight: 600;">● Active</span>
                        </div>
                        <div class="tx-item">
                            <div class="tx-icon-group">
                                <div class="tx-icon-circle" style="background: rgba(37, 99, 235, 0.15); color: #60a5fa;">🛡️</div>
                                <div>
                                    <div class="tx-title">Voice Biometrics Security</div>
                                    <div class="tx-time">Sarvam Saaras STT Verified</div>
                                </div>
                            </div>
                            <div style="font-size: 10px; font-weight: 700; color: #10b981;">SECURE</div>
                        </div>
                        <div class="tx-item">
                            <div class="tx-icon-group">
                                <div class="tx-icon-circle" style="background: rgba(245, 158, 11, 0.15); color: #fbbf24;">💳</div>
                                <div>
                                    <div class="tx-title">Card Daily Limit</div>
                                    <div class="tx-time">Contactless & Domestic POS</div>
                                </div>
                            </div>
                            <div style="font-size: 10px; font-weight: 700; color: #f8fafc;">₹ 1,00,000</div>
                        </div>
                        <div class="tx-item">
                            <div class="tx-icon-group">
                                <div class="tx-icon-circle" style="background: rgba(168, 85, 247, 0.15); color: #c084fc;">⭐</div>
                                <div>
                                    <div class="tx-title">Premier Privileges</div>
                                    <div class="tx-time">Diamond Tier Membership</div>
                                </div>
                            </div>
                            <div style="font-size: 10px; font-weight: 700; color: #fbbf24;">12,450 PTS</div>
                        </div>
                    </div>
                    """
                )

                # Voice Query Suggestions
                gr.HTML(
                    """
                    <div class="prompts-container">
                        <div style="font-size: 10px; font-weight: 700; color: #94a3b8; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 0.5px;">
                            💡 Suggested Voice Prompts
                        </div>
                        <div class="prompt-chip">🎙️ "What is my account balance?"</div>
                        <div class="prompt-chip">🎙️ "Show my transactions for the last 24 hours"</div>
                        <div class="prompt-chip">🎙️ "Did I get the refund from PQR Broadband?"</div>
                    </div>
                    """
                )

            # Right Column: Voice Concierge Console (Zero-Shift Static Cockpit)
            with gr.Column(scale=6, min_width=450, elem_id="right_panel_col"):
                # Voice Assistant Header with Live Status & Audio Waveform
                gr.HTML(
                    """
                    <div class="voice-agent-header">
                        <div class="agent-title-box">
                            <h3>🎙️ Aria — Premier Voice Assistant</h3>
                            <p class="agent-subtitle">Multilingual Sarvam Saaras STT & Bulbul TTS Neural Engine</p>
                        </div>
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <div id="audio_wave_visualizer" class="wave-container">
                                <div class="wave-bar"></div>
                                <div class="wave-bar"></div>
                                <div class="wave-bar"></div>
                                <div class="wave-bar"></div>
                                <div class="wave-bar"></div>
                            </div>
                            <span id="vad_status_badge" class="status-pill status-idle">
                                🟢 Ready • Tap Record to Speak
                            </span>
                        </div>
                    </div>
                    """
                )

                # Microphone Voice Trigger (Permanent Static Single Button)
                mic_input = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    elem_id="user_mic",
                    show_label=False,
                )

                # Hidden Background Voice Player (Autoplays with zero layout footprint)
                audio_output = gr.Audio(
                    type="filepath",
                    elem_id="assistant_audio",
                    autoplay=True,
                    interactive=False,
                    show_label=False,
                )

                # Live Conversation Transcript
                chatbot_display = gr.Chatbot(
                    label="💬 Live Conversation Transcript",
                    buttons=["copy"],
                    autoscroll=True,
                    elem_id="chatbot_display",
                    height=420,
                )

                # Session Utilities & Privacy Footer
                with gr.Row(elem_id="footer_row"):
                    clear_btn = gr.Button("🗑️ Reset Voice Session", elem_classes="clear-btn", scale=1)
                    gr.HTML(
                        """
                        <div style="display: flex; align-items: center; justify-content: flex-end; font-size: 10px; color: #64748b; height: 100%;">
                            🛡️ End-to-End Encrypted Voice Banking Session
                        </div>
                        """
                    )

        # Voice Trigger Wireup
        mic_input.stop_recording(
            fn=process_audio,
            inputs=[mic_input, chatbot_display],
            outputs=[chatbot_display, audio_output, mic_input],
        )

        # Clear Session Button Wireup
        clear_btn.click(
            fn=clear_session,
            inputs=[],
            outputs=[chatbot_display, audio_output, mic_input],
        )

    return demo


if __name__ == "__main__":
    demo = create_ui()
    demo.launch(theme=gr.themes.Soft(), css=BANKING_CSS, js=VAD_JAVASCRIPT, share=False)



# Sarvam AI Workshop: Building Voice & LLM Applications

Welcome to the **Sarvam AI Workshop** repository! This hands-on repository is designed to take you from foundational API calls to building production-ready, multimodal voice-to-voice chatbots and document intelligence pipelines using Sarvam AI and Gradio.

---

## 🚀 Environment Setup Guide

### 1. Clone the Repository & Navigate to Directory
```bash
git clone <repository-url>
cd sarvam
```

### 2. Create and Activate a Virtual Environment
- **macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- **Windows (Command Prompt / PowerShell)**:
  ```cmd
  python -m venv venv
  .\venv\Scripts\activate
  ```

### 3. Install Dependencies
Install all required libraries specified in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory (or update the existing `.env`) and add your API credentials:
```env
SARVAM_API_KEY=your_sarvam_api_key_here
# Optional (for multi-provider comparisons in Notebooks 07 & 10):
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

---

## 📚 Workshop Curriculum & Notebook Guide

The notebooks are designed to be followed sequentially:

| Notebook | Description |
| :--- | :--- |
| [01_hello_world.ipynb](./01_hello_world.ipynb) | Introduction to setting up the Sarvam AI client and making your first LLM chat completion API call. |
| [02_streaming_api.ipynb](./02_streaming_api.ipynb) | Demonstrates how to stream LLM responses chunk-by-chunk for low-latency, real-time output. |
| [03_simple_chatbot.ipynb](./03_simple_chatbot.ipynb) | Explains conversational memory by maintaining multi-turn chat history across user and assistant messages. |
| [04_chatbot_with_tools.ipynb](./04_chatbot_with_tools.ipynb) | Demonstrates tool/function calling with an LLM by integrating custom banking functions (`get_balance`, `get_transactions`). |
| [05_chatbot_with_streaming.ipynb](./05_chatbot_with_streaming.ipynb) | Combines tool/function calling with real-time response streaming for an interactive conversational assistant. |
| [06_chat_interface.ipynb](./06_chat_interface.ipynb) | Builds an interactive Gradio web UI connecting the tool-enabled banking chatbot for live user interaction. |
| [07_openai_interface.ipynb](./07_openai_interface.ipynb) | Shows how to use the OpenAI SDK interface as a unified abstraction across model providers (Sarvam AI, Groq, OpenAI). |
| [08_nlp_use_cases.ipynb](./08_nlp_use_cases.ipynb) | Explores practical NLP tasks including sentiment analysis and text summarization using structured LLM prompts. |
| [09_language_processing.ipynb](./09_language_processing.ipynb) | Covers Indic language processing including language detection, translation, and colloquial phrasing across Indian languages. |
| [10_comparing_token_usage.ipynb](./10_comparing_token_usage.ipynb) | Compares token efficiency and usage across different LLM providers (Sarvam AI, Groq, DeepSeek) for Indic language processing. |
| [11_text_to_speech.ipynb](./11_text_to_speech.ipynb) | Demonstrates text-to-speech (TTS) synthesis using Sarvam's Bulbul model across Indian languages and saving audio files. |
| [12_speech_to_text.ipynb](./12_speech_to_text.ipynb) | Demonstrates speech-to-text (STT) audio transcription using Sarvam's Saaras model. |
| [13_document_digitization.ipynb](./13_document_digitization.ipynb) | Demonstrates asynchronous document and handwritten text digitization/OCR using Sarvam's document intelligence APIs. |

---

## 🛠️ Applications & Code Challenge

### 🎙️ Voice-to-Voice AI Assistant (`code_challenge/solution/`)
A complete full-duplex voice chatbot application that combines:
- **Speech-to-Text (STT)**: Transcribes user microphone audio using `saaras:v3`.
- **Function-Calling Chatbot**: Banking agent capable of checking balances and recent transactions.
- **Text-to-Speech (TTS)**: Synthesizes spoken assistant responses using `bulbul:v3`.
- **Auto-Pause Detection (VAD)**: Automatically detects when you pause speaking and submits without manual clicking.
- **Responsive 2-Column Gradio UI**: Clean zero-scroll interface displaying live voice status, conversation history, and voice playback.

**To run the voice assistant application:**
```bash
python code_challenge/solution/app.py
```

---

## 📂 Repository Structure

```text
├── 01_hello_world.ipynb              # Getting started with Sarvam AI API
├── 02_streaming_api.ipynb            # Streaming API responses
├── 03_simple_chatbot.ipynb           # Multi-turn conversation history
├── 04_chatbot_with_tools.ipynb       # Function and tool calling
├── 05_chatbot_with_streaming.ipynb   # Tool calling with streaming
├── 06_chat_interface.ipynb          # Gradio web chat UI
├── 07_openai_interface.ipynb         # Multi-provider OpenAI SDK wrapper
├── 08_nlp_use_cases.ipynb            # Sentiment analysis & summarization
├── 09_language_processing.ipynb      # Language detection & Indic translation
├── 10_comparing_token_usage.ipynb    # Indic token usage comparison across LLMs
├── 11_text_to_speech.ipynb           # Bulbul TTS synthesis
├── 12_speech_to_text.ipynb           # Saaras STT transcription
├── 13_document_digitization.ipynb    # Document OCR & digitization
├── code_challenge/
│   ├── starter/                      # Starter template for hands-on challenge
│   └── solution/
│       ├── app.py                    # Voice-to-voice Gradio application
│       └── helper.py                 # Banking chatbot agent with tool handlers
├── data/
│   ├── audio/                        # Sample audio clips for STT
│   ├── pdfs/                         # Sample documents & forms for OCR
│   ├── sarvam_logo_pack/             # Sarvam AI branding assets
│   ├── script/                       # Sample dialogue scripts
│   └── text/                         # Sample text files
├── requirements.txt                  # Python dependencies
└── Readme.md                         # Workshop guide & navigation
```

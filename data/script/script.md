# Udemy Course Master Script: Building Voice & LLM Applications with Sarvam AI

**Course Title:** Building Voice & LLM Applications with Sarvam AI  
**Author / Instructor:** Course Production Team  
**Format:** Video Lectures + Hands-on Jupyter Notebooks + Slide Deck (`script.pptx`)  
**Target Audience:** Python Developers, AI Engineers, Data Scientists, and Tech Enthusiasts wanting to build Indic-language, Voice, and Multimodal AI systems.

---

# Course Outline & Module Breakdown

- **Module 1: Introduction & Foundation**
  - Lecture 00: Course Welcome & The Rise of Indian Sovereign AI
  - Lecture 01: Hello World – Environment Setup & Your First API Call (`01_hello_world.ipynb`)
  - Lecture 02: Streaming Responses for Low Latency (`02_streaming_api.ipynb`)
- **Module 2: Conversational AI, Tools & Web Interfaces**
  - Lecture 03: Multi-Turn Conversations & Persona Engineering (`03_simple_chatbot.ipynb`)
  - Lecture 04: Empowering LLMs with Function & Tool Calling (`04_chatbot_with_tools.ipynb`)
  - Lecture 05: Real-Time Streaming Chatbots with Tool Execution (`05_chatbot_with_streaming.ipynb`)
  - Lecture 06: Building an Interactive Gradio Web Chat UI (`06_chat_interface.ipynb`)
- **Module 3: NLP Applications & Multi-Provider Interoperability**
  - Lecture 07: Practical NLP: Sentiment Analysis & Summarization (`07_nlp_use_cases.ipynb`)
  - Lecture 08: Unified Multi-Provider Wrapper with OpenAI SDK (`08_openai_interface.ipynb`)
  - Lecture 09: Indic Language Detection, Translation & Colloquial Phrasing (`09_language_processing.ipynb`)
  - Lecture 10: Token Efficiency & Cost Comparison across Indic Models (`10_comparing_token_usage.ipynb`)
- **Module 4: Voice & Speech Intelligence**
  - Lecture 11: Text-to-Speech (TTS) Synthesis with Bulbul (`11_text_to_speech.ipynb`)
  - Lecture 12: Speech-to-Text (STT) Audio Transcription with Saaras (`12_speech_to_text.ipynb`)
- **Module 5: Document AI & Information Extraction**
  - Lecture 13: Asynchronous Document & Handwritten OCR Digitization (`13_document_digitization.ipynb`)
  - Lecture 14: Schema-Based Structured Document Extraction (`14_document_data_extraction.ipynb`)
- **Module 6: Capstone Project & Course Wrap-Up**
  - Lecture 15: Capstone: Full-Duplex Voice-to-Voice Banking Assistant (`code_challenge/`)
  - Lecture 16: Course Conclusion & Future Roadmap

---

# Module 1: Introduction & Foundation

## Lecture 00: Course Welcome & The Rise of Indian Sovereign AI

- **Video Duration:** ~3:30 min
- **Slide Reference:** Slides 1 – 4 in `script.pptx`

### 🎬 Visual Cues & Teleprompter Script

| Timestamp | Visual Cue / Slide | Teleprompter Script |
| :--- | :--- | :--- |
| **0:00 - 0:25** | **[Slide 1: Course Title & Instructor Camera]**<br>Warm smile, direct eye contact. | "Hello and welcome to **Building Voice & LLM Applications with Sarvam AI**! I’m thrilled to have you here. In this course, we are going to explore how to build next-generation, production-ready AI applications powered by India’s leading sovereign AI platform." |
| **0:25 - 0:55** | **[Slide 2: Global AI Landscape vs. India]**<br>Graphics showing OpenAI, Gemini, DeepSeek alongside Indian language scripts. | "Today, Artificial Intelligence is everywhere. It has become an indispensable part of our daily lives—powering web search, creative design, automated coding, data analytics, and customer support. We all recognize global names like OpenAI, Google’s Gemini, and DeepSeek. But almost all of these frontier models were designed and trained outside India with a predominantly Western linguistic baseline." |
| **0:55 - 1:35** | **[Slide 3: Meet Sarvam AI]**<br>Sarvam AI logo, Bengaluru HQ, key focus areas: Indic LLMs, Speech (STT/TTS), Vision/OCR. | "This begs the question: *Who is building world-class AI designed specifically for India's 1.4 billion people?*<br><br>The answer is **Sarvam AI**—a Bengaluru-based AI frontier lab pioneering Sovereign AI built *in* India, *for* India. While generic models often stumble on Indian scripts, regional accents, mixed colloquial phrasing (like Hinglish or Tanglish), and handwritten local documents, Sarvam’s models are purpose-built to excel in these exact domains." |
| **1:35 - 2:40** | **[Slide 4: Course Roadmap & Hands-On Projects]**<br>Interactive roadmap diagram covering the 6 modules. | "Throughout this course, we won’t just talk about theory—we will build practical, hands-on applications from scratch. Here is what we’ll master:<br><br>• **Conversational LLMs:** Real-time streaming, chat memory, and autonomous function/tool calling.<br>• **Indic Language Processing:** Language detection, translation, and classic vs. modern colloquial conversions.<br>• **Voice & Speech AI:** Studio-quality Text-to-Speech using Bulbul and lightning-fast Speech-to-Text using Saaras.<br>• **Document Intelligence:** Asynchronous OCR for printed & handwritten documents and schema-driven data extraction.<br>• **Capstone Project:** A complete voice-to-voice banking AI assistant with live voice activity detection in Gradio!" |
| **2:40 - 3:30** | **[Slide 4: Prerequisites & Setup Reminder + Camera]** | "All you need is basic Python knowledge and curiosity. In the next video, we’ll set up our environment, install dependencies, and make our very first API call with Sarvam AI. Let's get started!" |

---

## Lecture 01: Hello World – Environment Setup & Your First API Call

- **Video Duration:** ~4:30 min
- **Notebook Reference:** [`01_hello_world.ipynb`](file:///Users/vipar/Data/projects/sarvam/01_hello_world.ipynb)
- **Slide Reference:** Slide 5 in `script.pptx`

### 🎬 Visual Cues & Teleprompter Script

| Timestamp | Visual Cue / Action | Teleprompter Script |
| :--- | :--- | :--- |
| **0:00 - 0:30** | **[Camera + Slide 5: Hello World Overview]** | "Welcome to Lecture 1! In this video, we will set up our developer environment, load our credentials securely, and write our very first Python script using the official `sarvamai` SDK." |
| **0:30 - 1:15** | **[Screen Share: `01_hello_world.ipynb` - Cells 1 & 2]**<br>Highlight `load_dotenv()` and `assert SARVAM_API_KEY is not None`. | "Let’s open `01_hello_world.ipynb`. Security first: we never hardcode API keys inside source code. We use `python-dotenv` to read `SARVAM_API_KEY` from our local `.env` file. Notice our defensive assertion check: if the key is missing or empty, execution halts immediately with a clear error." |
| **1:15 - 2:30** | **[Screen Share: Cells 3 & 4]**<br>Highlight `from sarvamai import SarvamAI`, `client = SarvamAI(...)`, and `client.chat.completions(...)`. | "Now, let’s import `SarvamAI` and instantiate our `client` object with `api_subscription_key=SARVAM_API_KEY`.<br><br>To make a chat completion call, we call `client.chat.completions()`. We pass two core parameters:<br>1. `model`: We specify `sarvam-105b-conversations`—Sarvam’s high-capacity conversational model.<br>2. `messages`: A list of role-content dictionaries. Here, we send `{'role': 'user', 'content': 'Hi, How are you?'}`." |
| **2:30 - 3:30** | **[Screen Share: Run Cell 4 & Print Content]**<br>Show output text on screen. | "Let's run the cell! Within milliseconds, we extract the response via `response.choices[0].message.content`. The model politely greets us back." |
| **3:30 - 4:15** | **[Screen Share: Cell 5 - `response.model_dump_json(indent=2)`]**<br>Highlight `id`, `choices`, `finish_reason`, and `usage` object. | "Let's inspect the entire response payload using Pydantic’s `model_dump_json()`. Notice three key properties:<br>• `id`: Unique request trace ID.<br>• `choices[0].finish_reason`: Indicates `'stop'` when generation concludes normally.<br>• `usage`: Shows `prompt_tokens`, `completion_tokens`, and `total_tokens`. Monitoring tokens is vital for latency and cost tracking." |
| **4:15 - 4:30** | **[Camera: Instructor Wrap-up]** | "You’ve made your first successful API call! In the next lecture, we’ll explore how to stream responses chunk-by-chunk for lightning-fast user experiences." |

---

## Lecture 02: Streaming Responses for Low Latency

- **Video Duration:** ~4:00 min
- **Notebook Reference:** [`02_streaming_api.ipynb`](file:///Users/vipar/Data/projects/sarvam/02_streaming_api.ipynb)
- **Slide Reference:** Slide 6 in `script.pptx`

### 🎬 Visual Cues & Teleprompter Script

| Timestamp | Visual Cue / Action | Teleprompter Script |
| :--- | :--- | :--- |
| **0:00 - 0:40** | **[Slide 6: Blocking vs. Streaming Requests]**<br>Side-by-side comparison diagram of Time to First Token (TTFT). | "When generating long essays, code, or detailed explanations, waiting for the full response can cause 5 to 10 seconds of blank silence for users. In modern conversational apps, **streaming** is the industry standard. In this lecture, we’ll master streaming with Sarvam AI." |
| **0:40 - 1:40** | **[Screen Share: `02_streaming_api.ipynb` - Blocking Call]**<br>Ask for an essay on AI in Agriculture. Time the delay. | "First, let's observe a non-streaming call requesting a multi-paragraph response. Notice how the notebook waits patiently until all 300 words are generated before printing anything. Total perceived latency is around 4 seconds." |
| **1:40 - 2:50** | **[Screen Share: Streaming Call]**<br>Show `stream = client.chat.completions(..., stream=True)`. Run loop with `print(chunk.choices[0].delta.content or '', end='', flush=True)`. | "Now, let’s enable streaming! All we do is pass `stream=True`. Instead of returning a completed response object, the SDK returns a generator stream.<br><br>As we iterate over `stream`, each `chunk` delivers a tiny delta token. By using `print(..., end='', flush=True)`, the text flows onto the screen instantly as it is thought up by the model. The Time to First Token drops from 4 seconds down to under 300 milliseconds!" |
| **2:50 - 3:45** | **[Screen Share: Inspecting Individual Chunks]**<br>Step through `next(stream)` and print chunk JSONs. | "Let’s look under the hood with `next(stream)`. The first chunk sets up the structure and role. Subsequent chunks contain incremental strings under `choices[0].delta.content`. The final chunk contains `finish_reason: 'stop'`." |
| **3:45 - 4:00** | **[Camera: Instructor Wrap-up]** | "Streaming is crucial for interactive chat apps. Next, let’s learn how to build multi-turn conversational chatbots with memory." |

---

# Module 2: Conversational AI, Tools & Web Interfaces

## Lecture 03: Multi-Turn Conversations & Persona Engineering

- **Video Duration:** ~5:00 min
- **Notebook Reference:** [`03_simple_chatbot.ipynb`](file:///Users/vipar/Data/projects/sarvam/03_simple_chatbot.ipynb)
- **Slide Reference:** Slide 7 in `script.pptx`

### 🎬 Visual Cues & Teleprompter Script

| Timestamp | Visual Cue / Action | Teleprompter Script |
| :--- | :--- | :--- |
| **0:00 - 0:45** | **[Slide 7: Stateless LLMs vs. Conversational Memory]** | "LLMs are inherently stateless—they do not remember past requests on their own. To create a seamless conversational experience, we as developers must maintain and send the conversation history on every turn. In this lecture, we'll build a stateful chatbot and customize its behavior with system prompts." |
| **0:45 - 2:00** | **[Screen Share: `03_simple_chatbot.ipynb` - Context Window Demo]**<br>User: "My name is John." -> Next prompt: "What is my name?" | "Let’s test what happens if we don’t send context: if user says 'My name is John', and in a separate call we ask 'What is my name?', the model has no idea!<br><br>To give our chatbot memory, we maintain a `messages` list. Whenever the user speaks, we append `{'role': 'user', 'content': msg}`. When the model responds, we append `{'role': 'assistant', 'content': reply}` back into `messages` before sending the full array on the next turn." |
| **2:00 - 3:30** | **[Screen Share: Persona Engineering with System Prompt]**<br>Inject system prompt: "You are an enthusiastic cricket coach from Mumbai..." | "Now, let’s shape the AI’s personality using a `system` message at index 0. Let’s configure our bot as an enthusiastic cricket coach from Mumbai who incorporates colloquial Hindi expressions like *'Shabash!'* and *'Ekdum solid shot!'*.<br><br>When we ask a standard question like 'How do I play a cover drive?', observe how the tone instantly transforms to match our persona perfectly." |
| **3:30 - 4:45** | **[Screen Share: Interactive CLI Chat Loop]**<br>Run `run_chatbot()` loop with color-coded terminal text. | "We combine these concepts into a clean interactive command-line loop with colorized formatting. We can chat continuously, and the bot remembers everything discussed throughout the session." |
| **4:45 - 5:00** | **[Camera: Instructor Wrap-up]** | "Now that our bot has personality and memory, how can it take real-world actions like checking bank balances or booking tickets? That brings us to **Tool Calling** in Lecture 4!" |

---

## Lecture 04: Empowering LLMs with Function & Tool Calling

- **Video Duration:** ~6:00 min
- **Notebook Reference:** [`04_chatbot_with_tools.ipynb`](file:///Users/vipar/Data/projects/sarvam/04_chatbot_with_tools.ipynb)
- **Slide Reference:** Slide 8 in `script.pptx`

### 🎬 Visual Cues & Teleprompter Script

| Timestamp | Visual Cue / Action | Teleprompter Script |
| :--- | :--- | :--- |
| **0:00 - 0:50** | **[Slide 8: The Tool-Calling Loop Architecture]**<br>Diagram: User -> LLM decides tool call -> App executes Python function -> LLM summarizes result to User. | "LLMs cannot directly query your database or call external APIs on their own. Instead, they act as intelligent reasoning engines. With **Function Calling**, we describe available tools to the LLM using JSON schemas. When a user request requires data, the LLM outputs a structured tool request, we execute the Python function, and feed the result back to the model." |
| **0:50 - 2:00** | **[Screen Share: `04_chatbot_with_tools.ipynb` - Defining Python Functions & Tool Schemas]**<br>Show `get_balance(account_number)` and `get_transactions(account_number)`. | "Let’s build an AI Banking Assistant. We define two local Python helper functions: `get_balance` and `get_transactions`.<br><br>Then, we define the `tools` specification list adhering to the OpenAI-standard JSON schema. Each tool specifies its `name`, `description`, and parameter properties like `account_number`." |
| **2:00 - 3:30** | **[Screen Share: Invoking the LLM with `tools=tools`]**<br>User prompt: 'What is my balance in account 001002?' | "We pass `tools=tools` into `client.chat.completions()`. When the user asks: *'What is my balance in account 001002?'*, the model realizes it cannot guess a balance. Instead of generating regular text, `response.choices[0].message.tool_calls` contains a structured call for `get_balance` with argument `'{"account_number": "001002"}'`!" |
| **3:30 - 5:15** | **[Screen Share: Executing the Tool and Completing the Loop]**<br>Show `tools_map[func_name](**args)` and appending tool response message `{'role': 'tool', ...}`. | "Next, our application looks up the function in `tools_map`, runs it to get `{'balance': 15420.50, 'currency': 'INR'}`, and appends a `tool` message back to our conversation list.<br><br>We call the LLM one more time with the updated history. The model reads the tool output and crafts a friendly, natural reply: *'Your current balance for account 001002 is ₹15,420.50.'*" |
| **5:15 - 6:00** | **[Camera: Instructor Wrap-up]** | "This is the backbone of modern AI agents. In Lecture 5, we’ll combine tool execution with real-time token streaming!" |

---

## Lecture 05: Real-Time Streaming Chatbots with Tool Execution

- **Video Duration:** ~5:00 min
- **Notebook Reference:** [`05_chatbot_with_streaming.ipynb`](file:///Users/vipar/Data/projects/sarvam/05_chatbot_with_streaming.ipynb)
- **Slide Reference:** Slide 9 in `script.pptx`

### 🎬 Visual Cues & Teleprompter Script

| Timestamp | Visual Cue / Action | Teleprompter Script |
| :--- | :--- | :--- |
| **0:00 - 0:40** | **[Slide 9: Dual-Mode Execution: Tool Routing + Streaming]** | "In real-world production bots, users expect both capabilities: instant streaming text for conversational replies, and seamless tool execution when querying live systems. Let's see how to orchestrate both gracefully." |
| **0:40 - 2:30** | **[Screen Share: `05_chatbot_with_streaming.ipynb` - Chunk Aggregation Logic]**<br>Show accumulator variables: `tool_calls_accumulator` and `text_accumulator`. | "When streaming with tools enabled, the model might send text chunks OR tool call argument fragments. We maintain an accumulator loop. If `chunk.choices[0].delta.tool_calls` is present, we assemble the streaming function arguments. If regular content arrives, we immediately stream it to the screen." |
| **2:30 - 4:15** | **[Screen Share: Live Execution & Multi-Turn Test]**<br>Test query 1: 'Explain compounding interest' -> instant text stream.<br>Test query 2: 'Show my latest 3 transactions' -> runs tool -> streams summary. | "Let's watch this in action. When we ask a conceptual question, it streams instantly without tool calls. When we ask for recent transactions, it detects the tool call, displays an on-screen status `[Fetching transactions...]`, retrieves the data, and immediately streams the formatted bulleted list." |
| **4:15 - 5:00** | **[Camera: Instructor Wrap-up]** | "Now let's package our banking agent into a sleek web interface using Gradio in Lecture 6!" |

---

## Lecture 06: Building an Interactive Gradio Web Chat UI

- **Video Duration:** ~5:30 min
- **Notebook Reference:** [`06_chat_interface.ipynb`](file:///Users/vipar/Data/projects/sarvam/06_chat_interface.ipynb)
- **Slide Reference:** Slide 10 in `script.pptx`

### 🎬 Visual Cues & Teleprompter Script

| Timestamp | Visual Cue / Action | Teleprompter Script |
| :--- | :--- | :--- |
| **0:00 - 0:45** | **[Slide 10: Gradio Web Architecture]**<br>Gradio browser interface connected to Sarvam AI backend. | "Command-line interfaces are great for debugging, but end users need an intuitive, responsive web UI. In this lecture, we'll use Gradio to build a clean web chat interface for our tool-enabled Sarvam banking assistant." |
| **0:45 - 2:30** | **[Screen Share: `06_chat_interface.ipynb` - Chat Handler Function]**<br>Show `def chat(user_message, history)` and `handle_tool_call`. | "Gradio's `gr.ChatInterface` requires a handler function that accepts the current `user_message` and the conversation `history`.<br><br>We reconstruct the message list, prepend our banking system prompt, invoke Sarvam AI with tools enabled, and handle any function executions automatically." |
| **2:30 - 4:30** | **[Screen Share: Launching Gradio Web App & Testing Live]**<br>Run `chat_interface.launch(inline=True)` and open local browser URL. | "Let’s launch the interface! Notice how Gradio spins up a local web server with auto-scrolling chat bubbles, an input text box, retry buttons, and dark mode support.<br><br>Let’s type: *'Hi, can you check the balance for account 001002?'*. The bot calls our backend tool and displays the formatted balance inside the web browser in real time!" |
| **4:30 - 5:30** | **[Camera: Instructor Wrap-up]** | "With just ~40 lines of Python, you have a full-stack AI web app running locally! In Module 3, we’ll dive into NLP tasks, multilingual processing, and token cost economics." |

---

# Module 3: NLP Applications & Multi-Provider Interoperability

## Lecture 07: Practical NLP: Sentiment Analysis & Summarization

- **Video Duration:** ~4:30 min
- **Notebook Reference:** [`07_nlp_use_cases.ipynb`](file:///Users/vipar/Data/projects/sarvam/07_nlp_use_cases.ipynb)
- **Slide Reference:** Slide 11 in `script.pptx`

### 🎬 Visual Cues & Teleprompter Script

| Timestamp | Visual Cue / Action | Teleprompter Script |
| :--- | :--- | :--- |
| **0:00 - 0:45** | **[Slide 11: Enterprise NLP Workflows]**<br>Unstructured customer feedback -> Sentiment classification -> Executive summary. | "Beyond open-ended conversational bots, enterprises rely on LLMs for high-volume structured NLP tasks: analyzing customer feedback, classifying sentiment, and summarizing lengthy reports. In this lecture, we’ll implement both using prompt engineering." |
| **0:45 - 2:15** | **[Screen Share: `07_nlp_use_cases.ipynb` - Sentiment Analysis Batching]**<br>Highlight `feedback` list and `classify_feedback()` function with structured output prompt. | "Let’s look at a batch of mixed customer reviews for a banking mobile app. We craft a system prompt instructing the model to classify each review into `POSITIVE`, `NEGATIVE`, or `NEUTRAL` and extract the core root cause.<br><br>Let's run the batch. Notice how accurately the model tags bugs, UI complaints, and positive praise." |
| **2:15 - 3:45** | **[Screen Share: Multi-Document Summarization]**<br>Show `consolidated_feedback` string and executive summary generation. | "Next, we concatenate dozens of customer reviews into an aggregated feedback document and prompt the LLM for an executive bullet-point summary highlighting top feature requests and urgent bug fixes.<br><br>The model produces a concise, actionable report ready for product managers." |
| **3:45 - 4:30** | **[Camera: Instructor Wrap-up]** | "Structured prompting turns messy unstructured text into business insights. Next in Lecture 8, we’ll see how to switch seamlessly between model providers using the unified OpenAI SDK!" |

---

## Lecture 08: Unified Multi-Provider Wrapper with OpenAI SDK

- **Video Duration:** ~4:00 min
- **Notebook Reference:** [`08_openai_interface.ipynb`](file:///Users/vipar/Data/projects/sarvam/08_openai_interface.ipynb)
- **Slide Reference:** Slide 12 in `script.pptx`

### 🎬 Visual Cues & Teleprompter Script

| Timestamp | Visual Cue / Action | Teleprompter Script |
| :--- | :--- | :--- |
| **0:00 - 0:40** | **[Slide 12: Multi-Provider Abstraction Architecture]**<br>Diagram showing OpenAI Client targeting Sarvam AI, Groq, and OpenAI via `base_url`. | "In production systems, vendor lock-in is a real concern. What if you want to route queries dynamically between Sarvam AI, Groq, and OpenAI without rewriting your application logic? The OpenAI Python SDK has become the universal standard." |
| **0:40 - 2:30** | **[Screen Share: `08_openai_interface.ipynb` - Generic `call_llm` Function]**<br>Highlight `OpenAI(base_url=base_url, api_key=api_key)`. | "Because Sarvam AI exposes OpenAI-compatible REST endpoints, we can instantiate the standard `openai.OpenAI` client by passing Sarvam’s `base_url` and API subscription key.<br><br>Let’s write a generic helper function `call_llm(base_url, api_key, model, messages)`. The exact same function can now execute against Sarvam AI, Groq’s Llama models, or OpenAI models simply by swapping configuration parameters!" |
| **2:30 - 3:30** | **[Screen Share: Running multi-provider test calls]**<br>Execute Sarvam call, then Groq call with identical codebase. | "Let's run the notebook! Both providers respond seamlessly using the identical client invocation code. This gives you complete architectural flexibility in production." |
| **3:30 - 4:00** | **[Camera: Instructor Wrap-up]** | "Now let's explore one of Sarvam’s greatest strengths: deep Indic language processing in Lecture 9!" |

---

## Lecture 09: Indic Language Detection, Translation & Colloquial Phrasing

- **Video Duration:** ~5:30 min
- **Notebook Reference:** [`09_language_processing.ipynb`](file:///Users/vipar/Data/projects/sarvam/09_language_processing.ipynb)
- **Slide Reference:** Slide 13 in `script.pptx`

### 🎬 Visual Cues & Teleprompter Script

| Timestamp | Visual Cue / Action | Teleprompter Script |
| :--- | :--- | :--- |
| **0:00 - 0:50** | **[Slide 13: India's Multilingual Challenge]**<br>22 scheduled languages, multiple scripts, classic literary vs. modern colloquial styles. | "India has 22 scheduled languages and hundreds of dialects. Most international translation APIs produce stiff, overly formal textbook translations that sound unnatural to native speakers. Sarvam AI provides specialized language APIs that understand real-world Indian speech, scripts, and slang." |
| **0:50 - 2:15** | **[Screen Share: `09_language_processing.ipynb` - Language Identification]**<br>Highlight `client.text.identify_language(input=text)`. | "First, let's look at `client.text.identify_language()`. We feed it a string in Devanagari script: *'नमस्ते, आप कैसे हैं?'*. The API immediately returns the language code `hi-IN` and script identifier `Deva` with high confidence." |
| **2:15 - 3:45** | **[Screen Share: Bidirectional Translation]**<br>Translate Hindi to English, and English to Tamil / Telugu. | "Next, we use `client.text.translate()`. We translate our Hindi sentence into fluent English, and then translate English sentences into Tamil (`ta-IN`) and Bengali (`bn-IN`). Notice how grammatical agreement and gender inflections are preserved accurately." |
| **3:45 - 5:00** | **[Screen Share: Modern vs. Classic Colloquial Translation]**<br>Compare modern conversational vs formal translations. | "Look at this powerful capability: **Modern vs. Classic Colloquial modes**. When translating everyday conversational English like *'Hey, what's up? Where are you heading?'*, the classic mode gives formal literary phrasing, while the modern colloquial mode translates it into authentic, casual vernacular that real people speak every day." |
| **5:00 - 5:30** | **[Camera: Instructor Wrap-up]** | "This colloquial fidelity is game-changing for customer-facing chatbots. In Lecture 10, let's analyze how this efficiency impacts token usage and cost!" |

---

## Lecture 10: Token Efficiency & Cost Comparison across Indic Models

- **Video Duration:** ~4:30 min
- **Notebook Reference:** [`10_comparing_token_usage.ipynb`](file:///Users/vipar/Data/projects/sarvam/10_comparing_token_usage.ipynb)
- **Slide Reference:** Slide 14 in `script.pptx`

### 🎬 Visual Cues & Teleprompter Script

| Timestamp | Visual Cue / Action | Teleprompter Script |
| :--- | :--- | :--- |
| **0:00 - 0:50** | **[Slide 14: The Tokenization Problem in Indic Languages]**<br>Diagram showing Byte-Pair Encoding fragmentation: 1 Hindi word = 6 tokens on generic tokenizers vs. 1-2 tokens on Sarvam. | "Why do standard LLMs cost so much more and run slower when processing Indian languages? The secret lies in **Tokenization**. Most global tokenizers split non-Latin Unicode characters into multiple byte-level tokens. A single Hindi word might consume 6 tokens on a generic model, but only 1 or 2 tokens on Sarvam. Let's prove this with data." |
| **0:50 - 2:45** | **[Screen Share: `10_comparing_token_usage.ipynb` - Benchmark Script]**<br>Run identical Hindi prompt across Sarvam AI, Groq (Llama), and DeepSeek. | "In this notebook, we send the identical Hindi prompt: *'नमस्ते, आप कैसे हैं?'* across Sarvam AI and global models. We log `prompt_tokens` and `completion_tokens` from the usage payload for each provider." |
| **2:45 - 3:50** | **[Screen Share: Token Consumption Comparison Table]**<br>Highlight the dramatic difference in token counts. | "Look at the results! On standard tokenizers, the prompt and completion take 3x to 5x more tokens due to excessive sub-word splitting. On Sarvam’s native Indic tokenizer, token count is drastically lower. This means: **lower latency, longer effective context windows, and significantly lower API costs!**" |
| **3:50 - 4:30** | **[Camera: Instructor Wrap-up]** | "Now that we understand text and tokens, let's step into the world of Voice AI in Module 4!" |

---

# Module 4: Voice & Speech Intelligence

## Lecture 11: Text-to-Speech (TTS) Synthesis with Bulbul

- **Video Duration:** ~5:00 min
- **Notebook Reference:** [`11_text_to_speech.ipynb`](file:///Users/vipar/Data/projects/sarvam/11_text_to_speech.ipynb)
- **Slide Reference:** Slide 15 in `script.pptx`

### 🎬 Visual Cues & Teleprompter Script

| Timestamp | Visual Cue / Action | Teleprompter Script |
| :--- | :--- | :--- |
| **0:00 - 0:45** | **[Slide 15: Bulbul Text-to-Speech Model Architecture]**<br>Support for multiple Indian languages, speaker personas, and pitch/pace control. | "Voice is the most natural way millions of people across India interact with technology. Sarvam's **Bulbul** is a state-of-the-art neural Text-to-Speech engine crafted specifically for Indian accents, intonation, and multi-language pronunciation. Let's synthesize our first audio." |
| **0:45 - 2:30** | **[Screen Share: `11_text_to_speech.ipynb` - `client.text_to_speech.convert()`]**<br>Show text string, target language code, and voice selection. | "Let’s open `11_text_to_speech.ipynb`. We call `client.text_to_speech.convert()` passing our input text, target language (such as `en-IN` or `hi-IN`), and speaker voice ID.<br><br>The API synthesizes the audio and returns binary audio stream data." |
| **2:30 - 3:45** | **[Screen Share: Playing and Saving Audio]**<br>Play audio inside notebook using `IPython.display.Audio`. Run `save(audio, './data/audio/output1.wav')`. | "*[Play audio sample]* Listen to how natural and expressive that pacing sounds! There’s none of the robotic monotone common in generic TTS engines.<br><br>We can save this audio directly to a `.wav` file on disk for downstream use in our apps." |
| **3:45 - 5:00** | **[Camera: Instructor Wrap-up]** | "Now that our AI can speak, let's give it the ability to listen with Speech-to-Text in Lecture 12!" |

---

## Lecture 12: Speech-to-Text (STT) Audio Transcription with Saaras

- **Video Duration:** ~5:00 min
- **Notebook Reference:** [`12_speech_to_text.ipynb`](file:///Users/vipar/Data/projects/sarvam/12_speech_to_text.ipynb)
- **Slide Reference:** Slide 16 in `script.pptx`

### 🎬 Visual Cues & Teleprompter Script

| Timestamp | Visual Cue / Action | Teleprompter Script |
| :--- | :--- | :--- |
| **0:00 - 0:45** | **[Slide 16: Saaras Speech-to-Text Architecture]**<br>Acoustic modeling for Indian accents, background noise robustness, and code-mixed speech. | "Transcribing Indian speech is notoriously difficult due to diverse regional accents, background environmental noise, and code-switching between English and local languages. Sarvam's **Saaras** model is purpose-built to solve this." |
| **0:45 - 2:30** | **[Screen Share: `12_speech_to_text.ipynb` - Audio Transcription Function]**<br>Highlight `def transcribe_audio_to_text(audio_data)`. | "Let’s look at `12_speech_to_text.ipynb`. We create `transcribe_audio_to_text()` which reads raw audio bytes and sends them to Sarvam's STT endpoint.<br><br>Let’s test it with our generated `.wav` file from the previous lesson. The transcription comes back with 100% word accuracy and correct punctuation." |
| **2:30 - 4:15** | **[Screen Share: Interactive Gradio Audio Recorder]**<br>Show inline Gradio microphone widget. Record live voice: 'Hello, I want to check my account statement'. | "Now let's embed an interactive Gradio audio recording widget right inside Jupyter. We can click the microphone, speak directly into our laptop, and watch Saaras transcribe our live spoken words into text instantly!" |
| **4:15 - 5:00** | **[Camera: Instructor Wrap-up]** | "With STT and TTS, we have both sides of the voice pipeline. In Module 5, let's explore how to digitize and extract data from documents and handwriting!" |

---

# Module 5: Document AI & Information Extraction

## Lecture 13: Asynchronous Document & Handwritten OCR Digitization

- **Video Duration:** ~5:30 min
- **Notebook Reference:** [`13_document_digitization.ipynb`](file:///Users/vipar/Data/projects/sarvam/13_document_digitization.ipynb)
- **Slide Reference:** Slide 17 in `script.pptx`

### 🎬 Visual Cues & Teleprompter Script

| Timestamp | Visual Cue / Action | Teleprompter Script |
| :--- | :--- | :--- |
| **0:00 - 0:50** | **[Slide 17: Document Intelligence Architecture]**<br>PDF/Image upload -> Async Job Submission -> Polling Status -> Markdown & Table extraction. | "In enterprises across banking, insurance, healthcare, and government, millions of workflows still rely on physical paper, scanned PDFs, and handwritten notes. In this lecture, we'll use Sarvam's **Doc AI** to perform full-page OCR and convert messy documents into clean Markdown." |
| **0:50 - 2:30** | **[Screen Share: `13_document_digitization.ipynb` - Submitting Async Job]**<br>Show `client.doc_ai.digitise(...)` and extracting `job.job_id`. | "Document OCR is an asynchronous job-based process. We read our sample PDF (`feedback_notes.pdf`), submit it with `client.doc_ai.digitise()`, and receive a unique `job_id`.<br><br>We poll `client.doc_ai.get_status(job_id)` until the state transitions from `PENDING` to `SUCCESS`." |
| **2:30 - 4:30** | **[Screen Share: Downloading & Displaying Markdown Output]**<br>Show `client.doc_ai.get_download_url()`, extract ZIP payload, and render Markdown. | "Once complete, we get a secure download URL, unpack the resulting ZIP archive, and render the decoded Markdown.<br><br>Look at how cleanly it preserves headers, bullet points, and even messy handwritten doctor's notes and Hindi text documents!" |
| **4:30 - 5:30** | **[Camera: Instructor Wrap-up]** | "Digitizing text to Markdown is great, but what if you need specific structured JSON keys from an invoice or application form? That's **Schema-Based Extraction** in Lecture 14!" |

---

## Lecture 14: Schema-Based Structured Document Extraction

- **Video Duration:** ~5:00 min
- **Notebook Reference:** [`14_document_data_extraction.ipynb`](file:///Users/vipar/Data/projects/sarvam/14_document_data_extraction.ipynb)
- **Slide Reference:** Slide 18 in `script.pptx`

### 🎬 Visual Cues & Teleprompter Script

| Timestamp | Visual Cue / Action | Teleprompter Script |
| :--- | :--- | :--- |
| **0:00 - 0:45** | **[Slide 18: Unstructured Document to Strict JSON Schema]**<br>Sample bank letter / invoice -> Extracted JSON with fields: `applicant_name`, `account_no`, `requested_amount`. | "When building automated back-office pipelines, you need strict JSON schemas rather than freeform text. In this lecture, we'll extract structured data points directly from a scanned banking letter using Sarvam's schema extraction engine." |
| **0:45 - 2:30** | **[Screen Share: `14_document_data_extraction.ipynb` - Defining Extraction Schema]**<br>Show `schema = {'properties': {'sender_name': ..., 'account_number': ..., 'date': ...}}`. | "Let's inspect our target schema. We define the exact JSON fields we want the model to extract from `letter.pdf`: sender name, date, account number, reason for request, and branch name." |
| **2:30 - 4:15** | **[Screen Share: Submitting & Fetching Extracted JSON Results]**<br>Show `client.doc_ai.extract()`, poll status, and call `client.doc_ai.get_results()`. | "We submit the document alongside our schema via `client.doc_ai.extract()`. Once processed, `client.doc_ai.get_results(job_id)` returns a validated JSON object with all extracted fields perfectly populated!<br><br>No regular expressions or custom parsing required." |
| **4:15 - 5:00** | **[Camera: Instructor Wrap-up]** | "We have mastered LLMs, Tools, Speech, and Document AI. Now, it's time to bring everything together in our grand **Capstone Project** in Module 6!" |

---

# Module 6: Capstone Project & Course Wrap-Up

## Lecture 15: Capstone: Full-Duplex Voice-to-Voice Banking Assistant

- **Video Duration:** ~7:00 min
- **Code Reference:** [`code_challenge/solution/app.py`](file:///Users/vipar/Data/projects/sarvam/code_challenge/solution/app.py) & [`code_challenge/solution/helper.py`](file:///Users/vipar/Data/projects/sarvam/code_challenge/solution/helper.py)
- **Slide Reference:** Slide 19 in `script.pptx`

### 🎬 Visual Cues & Teleprompter Script

| Timestamp | Visual Cue / Action | Teleprompter Script |
| :--- | :--- | :--- |
| **0:00 - 1:00** | **[Slide 19: Capstone System Architecture]**<br>Microphone Audio -> Saaras STT -> Banking Chatbot Agent with Tool Calling -> Bulbul TTS -> Audio Speaker + Gradio UI. | "Welcome to the Capstone Project! In this lesson, we will build a complete **Voice-to-Voice AI Banking Assistant**. The user speaks into their mic, our app transcribes the audio with Saaras STT, routes the query through our function-calling banking agent, generates spoken audio with Bulbul TTS, and plays the voice reply back in a clean 2-column Gradio interface!" |
| **1:00 - 2:30** | **[Screen Share: Code Walkthrough - `helper.py`]**<br>Show banking tool handlers, session state management, and conversation routing. | "Let’s look at `helper.py`. We encapsulate our banking tools (`get_balance`, `get_transactions`), define the tool schema, and construct a robust multi-turn execution loop that seamlessly handles tool calls and returns assistant replies." |
| **2:30 - 4:30** | **[Screen Share: Code Walkthrough - `app.py`]**<br>Show Gradio Blocks layout, audio processing pipeline, and Voice Activity Detection (VAD). | "Now in `app.py`, we construct our Gradio web application. Notice the clean two-column layout: the left column houses the live microphone recorder and audio response player, while the right column shows the real-time chat history transcript.<br><br>When the user stops speaking, the audio pipeline transcribes the speech, invokes the banking agent, synthesizes the reply into `.wav` format, and plays it back automatically!" |
| **4:30 - 6:00** | **[Screen Share: Live End-to-End Voice Demo]**<br>Instructor speaks: *"Hello! Can you check the balance for account 001002?"*<br>Bot transcribes speech, runs tool, synthesizes voice: *"Your balance for account 001002 is ₹15,420.50."* | "Let’s test our live voice assistant! *[Demonstrate live voice conversation]*<br><br>Notice the zero-scroll clean design, instant voice feedback, and flawless function execution." |
| **6:00 - 7:00** | **[Camera: Instructor Wrap-up & Challenge]** | "You now have a fully functional multimodal voice assistant in your portfolio! You can find the starter template in `code_challenge/starter` to try building it yourself from scratch." |

---

## Lecture 16: Course Conclusion & Future Roadmap

- **Video Duration:** ~3:00 min
- **Slide Reference:** Slide 20 in `script.pptx`

### 🎬 Visual Cues & Teleprompter Script

| Timestamp | Visual Cue / Slide | Teleprompter Script |
| :--- | :--- | :--- |
| **0:00 - 0:45** | **[Slide 20: Course Summary & Key Achievements]**<br>Recap checklist: Setup, Streaming, Tools, Gradio UI, NLP, Multi-provider, Indic translation, TTS/STT, OCR, Voice Bot. | "Congratulations! You have officially completed **Building Voice & LLM Applications with Sarvam AI**! Take a moment to celebrate everything you’ve achieved." |
| **0:45 - 1:45** | **[Slide 20: What You Have Built]** | "Together, we covered:<br>• The Sarvam AI Python SDK and OpenAI interoperability<br>• Streaming chat completions and tool/function calling<br>• Real-world Indic translation with colloquial nuances<br>• High-accuracy Speech-to-Text and expressive Text-to-Speech<br>• Asynchronous Document OCR and schema extraction<br>• And an end-to-end full-duplex Voice-to-Voice AI Assistant!" |
| **1:45 - 2:30** | **[Camera: Next Steps & Encouragement]** | "Where should you go from here? Consider integrating Sarvam AI with vector databases like Chroma or Pinecone to build Indic Retrieval-Augmented Generation (RAG) systems, or deploying your Gradio applications to Hugging Face Spaces or AWS." |
| **2:30 - 3:00** | **[Slide 20: Final Slide + Rating / Review CTA]** | "Thank you so much for joining me on this journey. Please leave a rating and review if you enjoyed the course, and feel free to post your questions in the Q&A section. Keep building, and I wish you the best in your AI journey!" |

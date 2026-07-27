import os
import io
import json
import wave
import base64
import httpx
from typing import List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Import our dynamic ChatBot class
from placement_cell.chatbot import ChatBot

# Load API key and config from env
load_dotenv()
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# App definition
app = FastAPI(title="Placement Cell Voice Agent Portal")

# Paths for JSON databases
COMPANIES_FILE = os.path.join(os.path.dirname(__file__), "companies.json")
CV_FILE = os.path.join(os.path.dirname(__file__), "cv.json")

# Models for API
class Company(BaseModel):
    id: str
    name: str
    schedule: str
    slot: str
    eligibility: str
    cgpa_cutoff: float
    allowed_branches: List[str]

class StudentCV(BaseModel):
    name: str
    branch: str
    cgpa: float
    email: str
    skills: str

# Helper to read/write companies
def load_companies() -> List[Dict[str, Any]]:
    if not os.path.exists(COMPANIES_FILE):
        return []
    with open(COMPANIES_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_companies(companies: List[Dict[str, Any]]):
    with open(COMPANIES_FILE, "w") as f:
        json.dump(companies, f, indent=2)

# Helper to read/write CV
def load_cv() -> Dict[str, Any]:
    if not os.path.exists(CV_FILE):
        return {
            "name": "N/A",
            "branch": "N/A",
            "cgpa": 0.0,
            "email": "",
            "skills": ""
        }
    with open(CV_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_cv(cv_data: Dict[str, Any]):
    with open(CV_FILE, "w") as f:
        json.dump(cv_data, f, indent=2)

# PCM-to-WAV buffer conversion
def pcm_to_wav(pcm_data: bytes, sample_rate: int = 16000) -> bytes:
    wav_buf = io.BytesIO()
    with wave.open(wav_buf, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)   # 16-bit PCM (2 bytes)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)
    return wav_buf.getvalue()

# Sarvam AI STT Client
async def transcribe_audio(wav_bytes: bytes) -> str:
    if not SARVAM_API_KEY:
        print("SARVAM_API_KEY not configured.")
        return ""
    
    async with httpx.AsyncClient() as client:
        try:
            print("Sending request to Sarvam STT API...")
            response = await client.post(
                "https://api.sarvam.ai/speech-to-text",
                headers={
                    "api-subscription-key": SARVAM_API_KEY
                },
                files={
                    "file": ("audio.wav", wav_bytes, "audio/wav")
                },
                data={
                    "language_code": "en-IN",
                    "model": "saaras:v3"
                },
                timeout=30.0
            )
            if response.status_code == 200:
                result = response.json()
                transcript = result.get("transcript", "").strip()
                print(f"Sarvam STT success: '{transcript}'")
                return transcript
            else:
                print(f"Sarvam STT API returned error status {response.status_code}: {response.text}")
                return ""
        except Exception as e:
            print(f"Exception during STT API call: {e}")
            return ""

# Sarvam AI HTTP REST TTS Client
async def text_to_speech(text: str) -> str:
    if not SARVAM_API_KEY:
        print("SARVAM_API_KEY not configured for TTS.")
        return ""
    
    async with httpx.AsyncClient() as client:
        try:
            print(f"Sending request to Sarvam REST TTS API: '{text}'")
            response = await client.post(
                "https://api.sarvam.ai/text-to-speech",
                headers={
                    "api-subscription-key": SARVAM_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "text": text,
                    "target_language_code": "en-IN",
                    "speaker": "shubh",
                    "model": "bulbul:v3"
                },
                timeout=30.0
            )
            if response.status_code == 200:
                result = response.json()
                audios = result.get("audios", [])
                if audios:
                    print("Sarvam TTS success.")
                    return audios[0]  # Base64 string
            print(f"Sarvam TTS API returned error status {response.status_code}: {response.text}")
            return ""
        except Exception as e:
            print(f"Exception during TTS API call: {e}")
            return ""

# ----------------- CHATBOT TOOL FUNCTIONS -----------------

def get_upcoming_companies() -> str:
    """
    Returns upcoming IT companies schedule and qualifications as a formatted text string.
    """
    companies = load_companies()
    if not companies:
        return "There are no upcoming IT company interviews scheduled at the moment."
    
    lines = ["Here are the upcoming company recruitments:"]
    for c in companies:
        lines.append(f"- {c['name']} scheduled on {c['schedule']} (Slot: {c['slot']}). Eligibility: {c['eligibility']}.")
    return "\n".join(lines)

def check_eligibility_and_apply(company_name: str) -> str:
    """
    Validates student qualifications from system CV and registers application for the specified company.
    """
    companies = load_companies()
    matched_company = None
    for c in companies:
        if company_name.lower() in c["name"].lower() or c["id"].lower() in company_name.lower():
            matched_company = c
            break
            
    if not matched_company:
        return f"Company '{company_name}' was not found in the schedule. Please choose from Google, Microsoft, or Infosys."
    
    cv = load_cv()
    cgpa = cv.get("cgpa", 0.0)
    branch = cv.get("branch", "").upper().strip()
    
    cutoff = matched_company.get("cgpa_cutoff", 0.0)
    allowed = [b.upper().strip() for b in matched_company.get("allowed_branches", [])]
    
    # Validation logic
    if cgpa < cutoff:
        return f"Application Denied: Student CGPA is {cgpa}, which is below the minimum required {cutoff} for {matched_company['name']}."
    if allowed and branch not in allowed:
        return f"Application Denied: Student branch is {branch}, but {matched_company['name']} only accepts candidates from {', '.join(allowed)}."
        
    return f"Application Success: Student meets all qualifications for {matched_company['name']} (CGPA {cgpa}, Branch {branch}). Application submitted based on system CV."

def set_interview_reminder(company_name: str, time_slot: str) -> str:
    """
    Schedules an interview reminder notification.
    """
    return f"Success: Reminder scheduled for {company_name} interview slot starting at {time_slot}. The student will be alerted 30 minutes prior."

# Define JSON schemas of tools for LLM tool calling
placement_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_upcoming_companies",
            "description": "Retrieve details of all upcoming IT company interviews, including dates, timings, and qualification criteria.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_eligibility_and_apply",
            "description": "Check if the student meets a company's CGPA and branch cutoffs, and submit an application using their CV on the system.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "The name of the target IT company (e.g. Google, Microsoft, Infosys)"
                      }
                },
                "required": ["company_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_interview_reminder",
            "description": "Schedule a reminder notification for the student before their interview slot.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "The name of the company"
                    },
                    "time_slot": {
                        "type": "string",
                        "description": "The time slot of the interview (e.g. 10:00 AM - 12:00 PM)"
                    }
                },
                "required": ["company_name", "time_slot"]
            }
        }
    }
]

# ----------------- REST API ENDPOINTS -----------------

@app.get("/api/companies", response_model=List[Company])
def get_companies():
    return load_companies()

@app.post("/api/companies", response_model=Company)
def add_company(company: Company):
    companies = load_companies()
    if any(c["id"] == company.id for c in companies):
        raise HTTPException(status_code=400, detail="Company ID already exists")
    companies.append(company.model_dump())
    save_companies(companies)
    return company

@app.put("/api/companies/{company_id}", response_model=Company)
def update_company(company_id: str, updated_company: Company):
    companies = load_companies()
    for index, c in enumerate(companies):
        if c["id"] == company_id:
            companies[index] = updated_company.model_dump()
            save_companies(companies)
            return updated_company
    raise HTTPException(status_code=404, detail="Company not found")

@app.delete("/api/companies/{company_id}")
def delete_company(company_id: str):
    companies = load_companies()
    filtered = [c for c in companies if c["id"] != company_id]
    if len(filtered) == len(companies):
        raise HTTPException(status_code=404, detail="Company not found")
    save_companies(filtered)
    return {"detail": "Company deleted"}

@app.get("/api/cv", response_model=StudentCV)
def get_student_cv():
    return load_cv()

@app.post("/api/cv", response_model=StudentCV)
def update_student_cv(cv: StudentCV):
    save_cv(cv.model_dump())
    return cv

# ----------------- WEBSOCKET ENDPOINT -----------------

def create_chatbot() -> ChatBot:
    bot = ChatBot(
        api_key=DEEPSEEK_API_KEY,
        # model="sarvam-30b",
        model='deepseek-v4-flash',
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
            "Never respond in bullet points. It should look as though you are a human and having a conversation with a human."
        ),
        tools=placement_tools
    )
    bot.register_tool("get_upcoming_companies", get_upcoming_companies)
    bot.register_tool("check_eligibility_and_apply", check_eligibility_and_apply)
    bot.register_tool("set_interview_reminder", set_interview_reminder)
    return bot

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Retrieve connection mode ('voice' or 'text')
    mode = websocket.query_params.get("mode", "voice")
    await websocket.accept()
    
    pcm_buffer = bytearray()
    
    # Initialize the dynamic ChatBot instance for the connection session
    bot = create_chatbot()
    
    # Generate initial warm greeting from the LLM
    # try:
    #     greeting_text = bot.chat("Greet the student, explain you are the coordinator, and state the upcoming companies list.")
    # except Exception as e:
    #     print(f"ChatBot Initialization Error: {e}")
    #     greeting_text = "Welcome to the campus placement cell of Agni College of Technology. I am your coordinator. How can I help you get placed today?"
        
    # Only synthesize audio if the client requested 'voice' mode
    # if mode == "voice":
    #     greeting_audio = await text_to_speech(greeting_text)
    # else:
    #     greeting_audio = ""
    
    # await websocket.send_json({
    #     "event": "agent_speech",
    #     "text": greeting_text,
    #     "audio": greeting_audio,
    #     "stream": False,
    #     "state": "CHAT_ACTIVE"
    # })
    
    try:
        while True:
            message = await websocket.receive()
            
            # 1. Handle incoming binary audio packets
            if "bytes" in message:
                pcm_buffer.extend(message["bytes"])
                
            # 2. Handle incoming JSON control packets
            elif "text" in message:
                data = json.loads(message["text"])
                event = data.get("event")
                
                if event == "stop_recording":
                    if len(pcm_buffer) > 0:
                        # Convert accumulated PCM bytes to a WAV file bytes
                        wav_bytes = pcm_to_wav(bytes(pcm_buffer))
                        
                        # Clear buffer for the next round
                        pcm_buffer = bytearray()
                        
                        # Call Sarvam AI Speech-to-Text to transcribe user's audio
                        transcript = await transcribe_audio(wav_bytes)
                        
                        if transcript:
                            # Send transcribed text back to client for user bubble display
                            await websocket.send_json({
                                "event": "user_speech",
                                "text": transcript
                            })
                            
                            # Query ChatBot for the next turn
                            try:
                                bot_text = bot.chat(transcript)
                            except Exception as e:
                                print(f"ChatBot error: {e}")
                                bot_text = f"I encountered an issue processing your request: {e}"
                            
                            # Generate speech using Sarvam REST TTS API
                            base64_audio = await text_to_speech(bot_text)
                            
                            # Send response including the text and synthesized voice
                            await websocket.send_json({
                                "event": "agent_speech",
                                "text": bot_text,
                                "audio": base64_audio,
                                "stream": False,
                                "state": "CHAT_ACTIVE"
                            })
                        else:
                            await websocket.send_json({
                                "event": "agent_speech",
                                "text": "I couldn't hear you clearly. Could you please try repeating that?",
                                "audio": "",
                                "stream": False,
                                "state": "CHAT_ACTIVE"
                            })
                    else:
                        await websocket.send_json({
                            "event": "agent_speech",
                            "text": "No audio received. Try speaking while recording.",
                            "audio": "",
                            "stream": False,
                            "state": "CHAT_ACTIVE"
                        })
                        
                elif event == "cancel_recording":
                    pcm_buffer = bytearray()
                    print("DEBUG: Recording cancelled, cleared PCM buffer.")
                    
                elif event == "user_text":
                    user_msg = data.get("text", "").strip()
                    if user_msg:
                        try:
                            # Query chatbot directly (bypassing STT)
                            bot_text = bot.chat(user_msg)
                        except Exception as e:
                            print(f"ChatBot error: {e}")
                            bot_text = f"I encountered an issue processing your request: {e}"
                        
                        # Send text-only response back to client (bypassing TTS)
                        await websocket.send_json({
                            "event": "agent_speech",
                            "text": bot_text,
                            "audio": "",  # Empty string tells the client to skip TTS playback
                            "stream": False,
                            "state": "CHAT_ACTIVE"
                        })
                        
                elif event == "reset":
                    pcm_buffer = bytearray()
                    # Re-initialize the chatbot to wipe history
                    bot = create_chatbot()
                    
                    try:
                        greeting_text = bot.chat("Greet the student, explain you are the coordinator, and state the upcoming companies list.")
                    except Exception as e:
                        greeting_text = "Welcome to the campus placement cell of Agni College of Technology. I am your coordinator. How can I help you get placed today?"
                        
                    if mode == "voice":
                        greeting_audio = await text_to_speech(greeting_text)
                    else:
                        greeting_audio = ""
                        
                    await websocket.send_json({
                        "event": "agent_speech",
                        "text": greeting_text,
                        "audio": greeting_audio,
                        "stream": False,
                        "state": "CHAT_ACTIVE"
                    })
                    
    except WebSocketDisconnect:
        print("WebSocket client disconnected.")
    except Exception as e:
        print(f"WebSocket error: {e}")

# Mount static files
@app.get("/", response_class=HTMLResponse)
def get_index():
    static_index = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(static_index):
        with open(static_index, "r") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Placement Cell App</h1><p>Static index.html not found.</p>")

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

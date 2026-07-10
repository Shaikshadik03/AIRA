import sys
# 🕵️‍♂️ THE PYAUDIO HACK: Fools stubborn libraries into using our updated audio tool
try:
    import pyaudiowpatch as pyaudio
    sys.modules['pyaudio'] = pyaudio
except ImportError:
    pass

# --- EXTENSIONS LINKED HERE ---
import database
from system_control import SystemController
from profile_manager import ProfileManager
from app_launcher import AppLauncher
from note_manager import NoteManager
# ----------------------------------

import asyncio
import os
import aiohttp
import webbrowser
import subprocess
import sqlite3
import psutil
import pyttsx3
import speech_recognition as sr  
import threading                
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import uvicorn
import shutil

# Data blueprints for SaaS communication requests
class ChatPayload(BaseModel):
    message: str
    session_id: str = "default_session"
    conversation_title: str = "New Connection Frame"
    user: str = "Shaik Shadik"

DB_FILE = "aira_cloud_node.db"
NOTE_FILE = "aira_notes.txt"
UPLOAD_DIR = "uploads"

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize automation engines
sys_control = SystemController()
profile_mgr = ProfileManager()
launcher = AppLauncher()
note_mgr = NoteManager(NOTE_FILE)

def execute_native_voice_stream(text_to_speak: str):
    try:
        clean_speech = text_to_speak.replace("**", "").replace("`", "").replace("🚀", "").replace("📊", "")
        voice_engine = pyttsx3.init()
        voice_engine.setProperty('rate', 180)
        voice_engine.say(clean_speech)
        voice_engine.runAndWait()
    except Exception as e:
        print(f"❌ [Voice Engine Error] {str(e)}")

def continuous_ambient_ear_loop():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    try:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("\n📡 [Voice Node] Ambient ears armed. Listening for 'Hey AIRA'...")
            while True:
                try:
                    audio_packet = recognizer.listen(source, phrase_time_limit=4)
                    spoken_text = recognizer.recognize_google(audio_packet).lower().strip()
                    print(f"👂 [Audio Signal Detected]: '{spoken_text}'")
                    
                    if any(v in spoken_text for v in ["aira", "ira", "hey aira"]):
                        if "status" in spoken_text or "hardware" in spoken_text:
                            cpu_load = psutil.cpu_percent(interval=None)
                            report = f"Live CPU load is at {cpu_load} percent, Shadik."
                            execute_native_voice_stream(report)
                        elif "youtube" in spoken_text:
                            execute_native_voice_stream("Opening YouTube, Shadik.")
                            webbrowser.open("https://www.youtube.com")
                except sr.UnknownValueError:
                    pass
                except Exception:
                    pass
    except Exception as main_err:
        print(f"❌ [Voice Matrix Offline]: {str(main_err)}")

def init_memory_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT DEFAULT 'default_session',
            conversation_title TEXT DEFAULT 'New Chat',
            role TEXT,
            content TEXT,
            user_identity TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("💾 [Database Node] Local SaaS memory clusters initialized.")

def save_message_to_history(session_id: str, title: str, role: str, content: str, user_identity: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO system_chat_logs (session_id, conversation_title, role, content, user_identity) 
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, title, role, content, user_identity))
    conn.commit()
    conn.close()

def fetch_session_context(session_id: str, limit=10):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, content FROM system_chat_logs 
        WHERE session_id = ? ORDER BY id DESC LIMIT ?
    """, (session_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [{"role": role, "content": content} for role, content in reversed(rows)]

# MODERN LIFESPAN ARCHITECTURE
@asynccontextmanager
async def aira_application_lifespan(app: FastAPI):
    init_memory_database()
    database.init_db()
    
    print("⚡ Deploying Voiced Server Infrastructure with Background Ear Matrix...")
    listener_thread = threading.Thread(target=continuous_ambient_ear_loop, daemon=True)
    listener_thread.start()
    
    print("🚀 [Telegram/Discord Bot Nodes] Monitoring communication channels...")
    yield
    print("🔌 [Shutdown Matrix] Detaching core nodes gracefully.")

app = FastAPI(title="AIRA SaaS Core Engine", lifespan=aira_application_lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SIDEBAR ENGINE: Fetches unique list of past session metadata titles
@app.get("/sessions")
async def get_all_active_sessions():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT session_id, conversation_title, MAX(timestamp) 
            FROM system_chat_logs 
            GROUP BY session_id 
            ORDER BY timestamp DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [{"session_id": r[0], "title": r[1]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 📜 HISTORY GATEWAY: Pulls down all past messages for a clicked session
@app.get("/history/{session_id}")
async def get_session_history(session_id: str):
    """Retrieves all previous chat rows for a targeted workspace session."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT role, content FROM system_chat_logs 
            WHERE session_id = ? 
            ORDER BY id ASC
        """, (session_id,))
        rows = cursor.fetchall()
        conn.close()
        
        # Format back into frontend clean bubbles
        chat_bubbles = []
        for role, content in rows:
            sender = "AIRA" if role == "assistant" else "User"
            chat_bubbles.append({"sender": sender, "text": content})
            
        return chat_bubbles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def receive_remote_file(file: UploadFile = File(...)):
    try:
        destination_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(destination_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        asyncio.create_task(asyncio.to_thread(execute_native_voice_stream, f"File received: {file.filename}"))
        return {"status": "success", "saved_name": file.filename, "message": "Asset locked in vault storage."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def handle_flutter_chat(payload: ChatPayload):
    user_instruction = payload.message
    sender_name = payload.user
    sid = payload.session_id
    title = payload.conversation_title
    
    clean_cmd = user_instruction.lower().strip()
    
    # SYSTEM INTERCEPTS
    if "system status" in clean_cmd:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        report = f"📊 **Diagnostic Performance Matrix:**\n\n💻 CPU Load: {cpu}%\n🧠 RAM Allocation: {ram}%"
        return {"response": report}

    if "lock" in clean_cmd and "pc" in clean_cmd:
        res = sys_control.execute_action("lock")
        return {"response": f"🔒 OS Engine: {res}"}

    # STANDARD LLM ROUTING WITH TARGETED SESSION CONTEXT
    save_message_to_history(sid, title, "user", user_instruction, sender_name)
    chat_context = fetch_session_context(sid, limit=6)

    system_instruction = {"role": "system", "content": "You are AIRA, an enterprise SaaS dark-aesthetic core engine."}
    messages_payload = [system_instruction] + chat_context
    
    env_key = ""
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "GROQ_API_KEY" in line:
                    env_key = line.split("=")[1].strip().strip('"').strip("'")

    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {env_key}", "Content-Type": "application/json"}
        api_payload = {"model": "llama-3.1-8b-instant", "messages": messages_payload, "temperature": 0.4}
        try:
            async with session.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=api_payload, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    reply = data["choices"][0]["message"]["content"]
                    save_message_to_history(sid, title, "assistant", reply, "AIRA Engine")
                    asyncio.create_task(asyncio.to_thread(execute_native_voice_stream, reply))
                    return {"response": reply}
                return {"response": f"⚠️ Gateway status error: {response.status}"}
        except Exception as e:
            return {"response": f"📡 Pipeline transmission timeout: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
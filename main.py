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
import hashlib 
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import uvicorn
import shutil

# --- SECURITY SCHEME: Irreversible SHA-256 Password Hasher ---
def hash_user_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Data Blueprints for SaaS Request Processing
class RegisterPayload(BaseModel):
    username: str
    email: str
    password: str

class LoginPayload(BaseModel):
    email: str
    password: str

class ChatPayload(BaseModel):
    message: str
    session_id: str = "default_session"
    conversation_title: str = "New Connection Frame"
    user: str = "Anonymous User"

# ⚙️ NEW: Blueprint to parse configuration updates from your phone
class SettingsUpdatePayload(BaseModel):
    groq_api_key: str
    theme_accent: str = "Obsidian Slate"

DB_FILE = "aira_cloud_node.db"
NOTE_FILE = "aira_notes.txt"
UPLOAD_DIR = "uploads"

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
            print("\n📡 [Voice Node] Ambient ears armed. Listening...")
            while True:
                try:
                    audio_packet = recognizer.listen(source, phrase_time_limit=4)
                    spoken_text = recognizer.recognize_google(audio_packet).lower().strip()
                    if any(v in spoken_text for v in ["aira", "ira"]):
                        if "status" in spoken_text:
                            cpu_load = psutil.cpu_percent()
                            execute_native_voice_stream(f"Live CPU load is at {cpu_load} percent.")
                except Exception:
                    pass
    except Exception:
        print("❌ [Voice Matrix Offline]")

def init_memory_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # ⚙️ SETTINGS UPGRADE: Create a configurations table to hold active API keys and theme selections
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_settings (
            config_key TEXT PRIMARY KEY,
            config_value TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
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
    print("💾 [Database Node] Enterprise User Auth and Settings tables initialized.")

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
    cursor.execute("SELECT role, content FROM system_chat_logs WHERE session_id = ? ORDER BY id DESC LIMIT ?", (session_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [{"role": role, "content": content} for role, content in reversed(rows)]

# 🔄 DYNAMIC ROTATION CHECK: Queries the database first for updated API keys, falls back to .env
def fetch_active_groq_key() -> str:
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT config_value FROM system_settings WHERE config_key = 'groq_api_key'")
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0].strip():
            return row[0].strip()
    except Exception:
        pass
        
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "GROQ_API_KEY" in line:
                    return line.split("=")[1].strip().strip('"').strip("'")
    return ""

@asynccontextmanager
async def aira_application_lifespan(app: FastAPI):
    init_memory_database()
    database.init_db()
    print("⚡ Deploying Voiced Server Infrastructure with Background Ear Matrix...")
    listener_thread = threading.Thread(target=continuous_ambient_ear_loop, daemon=True)
    listener_thread.start()
    yield
    print("🔌 Detaching core nodes gracefully.")

app = FastAPI(title="AIRA SaaS Core Engine", lifespan=aira_application_lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⚙️ CONTROL GATEWAY 1: GET RUNTIME CONFIGURATIONS
@app.get("/settings")
async def get_current_system_settings():
    """Fetches saved API rotation flags and cosmetic configurations."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT config_key, config_value FROM system_settings")
        rows = cursor.fetchall()
        conn.close()
        
        settings_dict = {"groq_api_key": "", "theme_accent": "Obsidian Slate"}
        for r in rows:
            if r[0] == "groq_api_key":
                settings_dict["groq_api_key"] = r[1]
            elif r[0] == "theme_accent":
                settings_dict["theme_accent"] = r[1]
                
        return settings_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ⚙️ CONTROL GATEWAY 2: POST CONFIGURATION CHANGES
@app.post("/settings")
async def update_system_settings(payload: SettingsUpdatePayload):
    """Saves updated parameters directly to your laptop's database configuration registry."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO system_settings (config_key, config_value) 
            VALUES ('groq_api_key', ?)
        """, (payload.groq_api_key.strip(),))
        
        cursor.execute("""
            INSERT OR REPLACE INTO system_settings (config_key, config_value) 
            VALUES ('theme_accent', ?)
        """, (payload.theme_accent.strip(),))
        
        conn.commit()
        conn.close()
        print("⚙️ [Settings Applied] Updated operational parameters locked into database.")
        return {"status": "success", "message": "System parameters rotated and saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ⚙️ CONTROL GATEWAY 3: PURGE CHAT CACHE WIPE
@app.post("/database/clear")
async def clear_all_conversation_logs():
    """Wipes out all records in the system chat log table for a clean slate."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM system_chat_logs")
        conn.commit()
        conn.close()
        print("🧹 [System Purge Done] Clean slate execution triggered.")
        asyncio.create_task(asyncio.to_thread(execute_native_voice_stream, "System cache data cleared successfully, Shadik."))
        return {"status": "success", "message": "All database conversation log strings successfully purged."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🔐 AUTH ENDPOINTS
@app.post("/auth/register")
async def register_saas_user(payload: RegisterPayload):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (payload.email.strip().lower(),))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="This email channel is already registered.")
        hashed_pw = hash_user_password(payload.password)
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", (payload.username.strip(), payload.email.strip().lower(), hashed_pw))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "User registered cleanly."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/login")
async def login_saas_user(payload: LoginPayload):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password_hash FROM users WHERE email = ?", (payload.email.strip().lower(),))
    record = cursor.fetchone()
    conn.close()
    if not record or hash_user_password(payload.password) != record[1]:
        raise HTTPException(status_code=401, detail="Invalid account credentials.")
    return {"status": "success", "user": {"username": record[0], "email": payload.email.strip().lower()}}

@app.get("/sessions")
async def get_all_active_sessions():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT session_id, conversation_title, MAX(timestamp) FROM system_chat_logs GROUP BY session_id ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
        return [{"session_id": r[0], "title": r[1]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{session_id}")
async def get_session_history(session_id: str):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT role, content FROM system_chat_logs WHERE session_id = ? ORDER BY id ASC", (session_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{"sender": "AIRA" if r[0] == "assistant" else "User", "text": r[1]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def receive_remote_file(file: UploadFile = File(...)):
    try:
        destination_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(destination_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
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
    
    if "system status" in clean_cmd:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        return {"response": f"📊 **Performance Matrix:**\n\n💻 CPU: {cpu}%\n🧠 RAM: {ram}%"}

    save_message_to_history(sid, title, "user", user_instruction, sender_name)
    chat_context = fetch_session_context(sid, limit=6)
    system_instruction = {"role": "system", "content": "You are AIRA, an enterprise SaaS dark-aesthetic core assistant."}
    messages_payload = [system_instruction] + chat_context
    
    # Use our newly added dynamic API check function!
    env_key = fetch_active_groq_key()

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
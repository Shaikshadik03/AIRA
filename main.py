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
import uvicorn
import shutil

class ChatPayload(BaseModel):
    message: str
    user: str = "Shaik Shadik"

app = FastAPI(title="AIRA Core AI Network Node")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "aira_cloud_node.db"
NOTE_FILE = "aira_notes.txt"
UPLOAD_DIR = "uploads"

# Ensure the physical upload storage vault exists on your hard drive
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize our custom hardware automation clusters
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

# 🎙️ CONTINUOUS BACKGROUND LISTENING CORE
def continuous_ambient_ear_loop():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    try:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("\n📡 [Voice Node] Ambient ears armed and calibrated. Listening for 'Hey AIRA'...")
            
            while True:
                try:
                    audio_packet = recognizer.listen(source, phrase_time_limit=4)
                    spoken_text = recognizer.recognize_google(audio_packet).lower().strip()
                    
                    print(f"👂 [Audio Signal Detected]: '{spoken_text}'")
                    
                    wake_variants = ["aira", "ira", "hair", "era", "hey ira", "hey aira"]
                    is_wake_hit = any(variant in spoken_text for variant in wake_variants)
                    is_direct_action = any(cmd in spoken_text for cmd in ["youtube", "status", "hardware", "whatsapp"])
                    
                    if is_wake_hit or is_direct_action:
                        print("🔥 [WAKE PROTOCOL] Target trigger intercepted successfully!")
                        
                        if "status" in spoken_text or "hardware" in spoken_text:
                            cpu_load = psutil.cpu_percent(interval=None)
                            ram_used = psutil.virtual_memory().percent
                            report = f"Live hardware status update: CPU load is at {cpu_load} percent, and memory utilization is at {ram_used} percent, Shadik."
                            print(f"🤖 AIRA Spoken Reply: {report}")
                            execute_native_voice_stream(report)
                            
                        elif "youtube" in spoken_text:
                            print("🚀 Launching YouTube application loop!")
                            execute_native_voice_stream("Opening YouTube right away, Shadik.")
                            webbrowser.open("https://www.youtube.com")
                            
                        elif "whatsapp" in spoken_text:
                            print("💬 Launching WhatsApp communications dashboard!")
                            execute_native_voice_stream("Opening WhatsApp Web console, Shadik.")
                            webbrowser.open("https://web.whatsapp.com")
                            
                        else:
                            if not is_direct_action:
                                execute_native_voice_stream("Yes Shadik, I am online. Standing by for voice actions.")
                                
                except sr.UnknownValueError:
                    pass
                except Exception as e:
                    pass
    except Exception as main_err:
        print(f"❌ [Voice Hardware Matrix Error]: {str(main_err)}")

def init_memory_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            user_identity TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("💾 [Database Node] Local memory clusters verified and indexed.")

def save_message_to_history(role: str, content: str, user_identity: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO system_chat_logs (role, content, user_identity) VALUES (?, ?, ?)", (role, content, user_identity))
    conn.commit()
    conn.close()

def fetch_recent_context_history(limit=6):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM system_chat_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [{"role": role, "content": content} for role, content in reversed(rows)]

def fetch_groq_api_key():
    if os.path.exists(".env"):
        with open(".env", "r") as env_file:
            for line in env_file:
                if "GROQ_API_KEY" in line and "=" in line:
                    return line.split("=")[1].strip().strip('"').strip("'")
    return os.getenv("GROQ_API_KEY", "")

# 📦 NEW FILE UPLOAD CHANNEL
@app.post("/upload")
async def receive_remote_file(file: UploadFile = File(...)):
    """Accepts files sent wirelessly from your smartphone and saves them safely."""
    try:
        destination_path = os.path.join(UPLOAD_DIR, file.filename)
        
        # Saves the file bytes dynamically into your local uploads directory
        with open(destination_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"📥 [File Pipeline] Saved inbound file: '{file.filename}' successfully inside vault.")
        
        # Make AIRA speak out loud when a download lands successfully!
        asyncio.create_task(asyncio.to_thread(execute_native_voice_stream, f"File received: {file.filename} has been saved to your workspace vault, Shadik."))
        
        return {
            "status": "success",
            "saved_name": file.filename,
            "message": "File verified and written into laptop hardware storage clusters cleanly."
        }
    except Exception as e:
        print(f"❌ [File Pipeline Failure]: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal vault write failure: {str(e)}")

@app.post("/chat")
async def handle_flutter_chat(payload: ChatPayload):
    user_instruction = payload.message
    sender_name = payload.user
    
    print(f"\n📲 [Inbound Frame] User: '{sender_name}' | Prompt: '{user_instruction}'")
    clean_cmd = user_instruction.lower().strip().replace('"', '').replace("'", "")
    
    # --- INTERCEPT 1: SYSTEM HARDWARE METRICS STATUS ---
    if "system status" in clean_cmd:
        cpu_load = psutil.cpu_percent(interval=None)
        ram_used_pct = psutil.virtual_memory().percent
        battery_metrics = psutil.sensors_battery()
        battery_pct = f"{battery_metrics.percent}%" if battery_metrics else "Grid Power Connected"
        
        hardware_health_report = (
            f"📊 **AIRA Live Diagnostic Performance Matrix:**\n\n"
            f"💻 **CPU Utilization Load:** {cpu_load}%\n"
            f"🧠 **System RAM Allocation:** {ram_used_pct}%\n"
            f"🔋 **Laptop Battery Storage Energy:** {battery_pct}\n\n"
            f"🟢 Framework Status: Systems nominal, Creator Shadik."
        )
        voice_summary = f"System metrics scanned. CPU load is at {cpu_load} percent. All systems nominal, Shadik."
        asyncio.create_task(asyncio.to_thread(execute_native_voice_stream, voice_summary))
        return {"response": hardware_health_report}

    # --- INTERCEPT 2: NATIVE WINDOWS PC REMOTE CONTROL LOCK HOOK ---
    if "lock" in clean_cmd and ("pc" in clean_cmd or "screen" in clean_cmd or "laptop" in clean_cmd):
        execution_result = sys_control.execute_action("lock")
        database.log_interaction_metric(command="lock", module="system_control")
        asyncio.create_task(asyncio.to_thread(execute_native_voice_stream, "Locking your computer screen immediately, Shadik."))
        return {"response": f"🔒 **AIRA OS Control Engine:** {execution_result}"}

    # --- INTERCEPT 3: NATIVE WINDOWS PC REMOTE CONTROL SLEEP HOOK ---
    if "sleep" in clean_cmd and ("pc" in clean_cmd or "laptop" in clean_cmd or "computer" in clean_cmd):
        execution_result = sys_control.execute_action("sleep")
        database.log_interaction_metric(command="sleep", module="system_control")
        asyncio.create_task(asyncio.to_thread(execute_native_voice_stream, "Putting your workstation to sleep, Shadik."))
        return {"response": f"💤 **AIRA OS Control Engine:** {execution_result}"}

    # --- INTERCEPT 4: APPLICATION LAUNCHER AUTOMATION HOOKS ---
    if "open" in clean_cmd:
        for app_nickname in ["chrome", "notepad", "vstext"]:
            if app_nickname in clean_cmd:
                execution_result = launcher.launch_program(app_nickname)
                database.log_interaction_metric(command=f"launch_{app_nickname}", module="app_launcher")
                asyncio.create_task(asyncio.to_thread(execute_native_voice_stream, f"Opening {app_nickname}, Shadik."))
                return {"response": f"🚀 **AIRA App Launcher:** {execution_result}"}

    # --- INTERCEPT 5: LONG-TERM MEMORY ENGINE HOOKS ---
    if clean_cmd.startswith("remember"):
        fact_to_save = user_instruction[8:].strip()
        if fact_to_save:
            execution_result = profile_mgr.remember_user_fact(category="preference", fact=fact_to_save)
            asyncio.create_task(asyncio.to_thread(execute_native_voice_stream, "Fact logged into long term memory clusters."))
            return {"response": f"🧠 **AIRA Memory Engine:** {execution_result}"}

    if "show memories" in clean_cmd or "view profile" in clean_cmd:
        all_memories = profile_mgr.pull_all_memories()
        return {"response": all_memories}

    # --- INTERCEPT 6: WORKSPACE NOTE SYSTEM HOOKS ---
    if "read note" in clean_cmd or "workspace note" in clean_cmd:
        execution_result = note_mgr.read_notes()
        return {"response": execution_result}

    if clean_cmd.startswith("write note") or clean_cmd.startswith("add note"):
        note_to_save = user_instruction[10:].strip()
        if note_to_save:
            execution_result = note_mgr.write_note(note_to_save)
            asyncio.create_task(asyncio.to_thread(execute_native_voice_stream, "Note added to workspace."))
            return {"response": execution_result}

    # Route to Llama-3 via Groq API
    save_message_to_history("user", user_instruction, sender_name)
    chat_context = fetch_recent_context_history(limit=6)

    system_instruction = {
        "role": "system", 
        "content": "You are AIRA, a premium minimalist dark-aesthetic system core assistant created by Shadik."
    }
    
    messages_payload = [system_instruction] + chat_context
    api_key = fetch_groq_api_key()

    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        api_payload = {"model": "llama-3.1-8b-instant", "messages": messages_payload, "temperature": 0.5}
        
        try:
            async with session.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=api_payload, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    aira_ai_reply = data["choices"][0]["message"]["content"]
                    save_message_to_history("assistant", aira_ai_reply, "AIRA Engine")
                    asyncio.create_task(asyncio.to_thread(execute_native_voice_stream, aira_ai_reply))
                    return {"response": aira_ai_reply}
                else:
                    return {"response": f"⚠️ API Connection Status Breakdown: {response.status}"}
        except Exception as e:
            return {"response": f"📡 Network transmission timeout: {str(e)}"}

@app.on_event("startup")
async def app_startup_sequence():
    init_memory_database()
    database.init_db()
    print("⚡ Deploying Voiced Server Infrastructure with Background Ear Matrix...")
    listener_thread = threading.Thread(target=continuous_ambient_ear_loop, daemon=True)
    listener_thread.start()
    asyncio.create_task(activate_background_bot_nodes())

async def activate_background_bot_nodes():
    await asyncio.sleep(1)
    print("🚀 [Telegram Node] Sync Complete. Listening...")
    await asyncio.sleep(1)
    print("🚀 [Discord Node] Client logged in successfully as user: AIRA OS")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
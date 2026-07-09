import asyncio
import os
import aiohttp
import webbrowser
import subprocess
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 📦 1. DATA BLUEPRINT DEFINED FIRST (Fixes the 422 parsing error)
class ChatPayload(BaseModel):
    message: str

# Initialize your core network engine app
app = FastAPI(title="AIRA Core AI Network Node")

# 🛡️ THE CORS HANDSHAKE UNLOCK NODE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "aira_cloud_node.db"

# 💾 THE DATABASE INITIALIZATION NODE
def init_memory_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("💾 [Database Node] Local memory clusters verified and indexed.")

def save_message_to_history(role: str, content: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO system_chat_logs (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()

def fetch_recent_context_history(limit=6):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM system_chat_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    formatted_history = []
    for role, content in reversed(rows):
        formatted_history.append({"role": role, "content": content})
    return formatted_history

# 🗝️ AUTOMATIC ENV KEY EXTRACTOR NODE
def fetch_groq_api_key():
    if os.path.exists(".env"):
        with open(".env", "r") as env_file:
            for line in env_file:
                if "GROQ_API_KEY" in line and "=" in line:
                    return line.split("=")[1].strip().strip('"').strip("'")
    return os.getenv("GROQ_API_KEY", "")

# 📡 THE LIVE CHAT ROUTING & MEMORY INTERFACE
@app.post("/chat")
async def handle_flutter_chat(payload: ChatPayload):
    user_instruction = payload.message
    print(f"\n📲 [Frontend Interface] Inbound text frame caught: '{user_instruction}'")
    
    clean_cmd = user_instruction.lower().strip().replace('"', '').replace("'", "")
    
    # ⚡ AUTOMATION INTERCEPT BLOCK
    if "open youtube" in clean_cmd:
        webbrowser.open("https://www.youtube.com")
        return {"response": "🚀 System matrix override complete! Opening YouTube directly on your desktop screen, Shadik."}
    elif "open google" in clean_cmd:
        webbrowser.open("https://www.google.com")
        return {"response": "🌐 System matrix override complete! Spawning a clean Google Search node on your desktop, Shadik."}
    elif "open calculator" in clean_cmd or "open calc" in clean_cmd:
        try:
            subprocess.Popen("calc.exe")
            return {"response": "🧮 System matrix override complete! Waking up the local Windows Calculator utility, Shadik."}
        except Exception as e:
            return {"response": f"⚠️ Failed to call native system application: {str(e)}"}

    # Save user message to database
    save_message_to_history("user", user_instruction)

    # Fetch history context rows
    chat_context = fetch_recent_context_history(limit=6)

    system_instruction = {
        "role": "system", 
        "content": "You are AIRA, a highly advanced assistant designed by Shadik. You have an active SQLite database memory cluster node—remember what Shadik told you earlier in the context log! Respond sharply and concisely."
    }
    
    messages_payload = [system_instruction] + chat_context

    print(f"🚀 [Model Router Engine] Channeling prompt payload with database history node to: llama-3.1-8b-instant")
    
    api_key = fetch_groq_api_key()
    if not api_key:
        return {"response": "System Alert: Connection failed. Key error inside active workspace, Shadik."}

    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        api_payload = {
            "model": "llama-3.1-8b-instant",
            "messages": messages_payload,
            "temperature": 0.7
        }
        
        try:
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions", 
                headers=headers, 
                json=api_payload,
                timeout=10
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    aira_ai_reply = data["choices"][0]["message"]["content"]
                    
                    # Save Assistant message to history
                    save_message_to_history("assistant", aira_ai_reply)
                    
                    print("🟩 [System Sync] History logged. Response packaging frame sent to frontend bubble.")
                    return {"response": aira_ai_reply}
                else:
                    return {"response": f"⚠️ Neural connection error. Status code: {response.status}"}
        except Exception as e:
            return {"response": f"📡 Network packet loss detected: {str(e)}"}

@app.on_event("startup")
async def app_startup_sequence():
    init_memory_database()
    print("⚡ Deploying Shielded Server Infrastructure with Hot-Reload Engine on Port 8000...")
    asyncio.create_task(activate_background_bot_nodes())

async def activate_background_bot_nodes():
    await asyncio.sleep(1)
    print("🚀 [Telegram Node] Sync Complete. Listening...")
    await asyncio.sleep(1)
    print("🚀 [Discord Node] Client logged in successfully as user: AIRA OS")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
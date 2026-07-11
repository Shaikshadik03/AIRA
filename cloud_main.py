import os
import aiohttp
import sqlite3
import hashlib
import asyncio
from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import uvicorn
import shutil

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

class SettingsUpdatePayload(BaseModel):
    groq_api_key: str
    theme_accent: str = "Obsidian Slate"

DB_FILE = "aira_cloud_v2.db"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def hash_user_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def init_cloud_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_settings (
            config_key TEXT PRIMARY KEY, config_value TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT DEFAULT 'default_session',
            conversation_title TEXT DEFAULT 'New Chat',
            role TEXT, content TEXT, user_identity TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("💾 [Cloud Core] Database infrastructure mapped cleanly with full columns.")

def save_message_to_history(session_id: str, title: str, role: str, content: str, user_identity: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO system_chat_logs (session_id, conversation_title, role, content, user_identity) 
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, title, role, content, user_identity))
    conn.commit()
    conn.close()

def fetch_session_context(session_id: str, limit=6):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM system_chat_logs WHERE session_id = ? ORDER BY id DESC LIMIT ?", (session_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [{"role": role, "content": content} for role, content in reversed(rows)]

def fetch_active_groq_key() -> str:
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT config_value FROM system_settings WHERE config_key = 'groq_api_key'")
        row = cursor.fetchone()
        conn.close()
        if row and row[0].strip(): return row[0].strip()
    except Exception: pass
    return os.getenv("GROQ_API_KEY", "")

@asynccontextmanager
async def cloud_application_lifespan(app: FastAPI):
    init_cloud_database()
    yield

app = FastAPI(title="AIRA Cloud Core Gateway", lifespan=cloud_application_lifespan)

@app.get("/")
async def cloud_health_check():
    return {"status": "online", "matrix": "AIRA OS SaaS Core Live Node"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

agent_websocket: WebSocket = None
pending_futures = {}

@app.websocket("/ws/agent")
async def agent_tunnel_endpoint(websocket: WebSocket):
    global agent_websocket
    await websocket.accept()
    agent_websocket = websocket
    try:
        while True:
            inbound_payload = await websocket.receive_json()
            cmd_id = inbound_payload.get("id")
            if cmd_id in pending_futures:
                pending_futures[cmd_id].set_result(inbound_payload.get("result"))
    except WebSocketDisconnect:
        pass
    finally:
        agent_websocket = None

@app.post("/auth/register")
async def register_saas_user(payload: RegisterPayload):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (payload.email.strip().lower(),))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="This email channel is already registered.")
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", (payload.username.strip(), payload.email.strip().lower(), hash_user_password(payload.password)))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "User registered."}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

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
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT session_id, conversation_title, MAX(timestamp) FROM system_chat_logs GROUP BY session_id ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"session_id": r[0], "title": r[1]} for r in rows]

@app.get("/history/{session_id}")
async def get_session_history(session_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM system_chat_logs WHERE session_id = ? ORDER BY id ASC", (session_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"sender": "AIRA" if r[0] == "assistant" else "User", "text": r[1]} for r in rows]

@app.post("/settings")
async def update_system_settings(payload: SettingsUpdatePayload):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO system_settings (config_key, config_value) VALUES ('groq_api_key', ?)", (payload.groq_api_key.strip(),))
    cursor.execute("INSERT OR REPLACE INTO system_settings (config_key, config_value) VALUES ('theme_accent', ?)", (payload.theme_accent.strip(),))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/database/clear")
async def clear_all_conversation_logs():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM system_chat_logs")
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/chat")
async def handle_flutter_chat(payload: ChatPayload):
    try:
        global agent_websocket
        user_instruction = payload.message
        sender_name = payload.user
        sid = payload.session_id
        title = payload.conversation_title
        clean_cmd = user_instruction.lower().strip()
        
        if any(keyword in clean_cmd for keyword in ["system status", "lock", "sleep", "open", "volume", "mute", "play", "pause"]):
            if not agent_websocket:
                return {"response": "📡 **Hardware Agent Offline:** Your cloud cluster is active, but your laptop agent is disconnected."}
                
            cmd_id = str(asyncio.get_running_loop().time())
            future = asyncio.get_running_loop().create_future()
            pending_futures[cmd_id] = future
            
            try:
                await agent_websocket.send_json({"id": cmd_id, "action": clean_cmd})
                result_string = await asyncio.wait_for(future, timeout=6.0)
                return {"response": result_string}
            except asyncio.TimeoutError:
                return {"response": "⚠️ **Transmission Timeout:** Local agent did not reply in time."}
            finally:
                pending_futures.pop(cmd_id, None)

        save_message_to_history(sid, title, "user", user_instruction, sender_name)
        chat_context = fetch_session_context(sid, limit=6)
        messages_payload = [{"role": "system", "content": "You are AIRA, an enterprise SaaS dark-aesthetic core assistant."}] + chat_context
        
        env_key = fetch_active_groq_key()
        
        if not env_key or len(env_key) < 10:
            return {"response": "🔑 **Groq API Key Missing:** Please open the mobile app Sidebar Drawer ➔ System Settings, paste your valid API key, and tap save."}

        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {env_key}", "Content-Type": "application/json"}
            api_payload = {"model": "llama-3.1-8b-instant", "messages": messages_payload, "temperature": 0.4}
            async with session.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=api_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    reply = data["choices"][0]["message"]["content"]
                    save_message_to_history(sid, title, "assistant", reply, "AIRA Engine")
                    return {"response": reply}
                else:
                    err_text = await response.text()
                    return {"response": f"⚠️ **Groq API Error ({response.status}):** Check if your key is active. Details: {err_text[:100]}"}
    except Exception as global_error:
        return {"response": f"❌ **Internal Cloud Core Exception:** {str(global_error)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
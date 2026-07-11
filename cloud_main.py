import os
import aiohttp
import sqlite3
import hashlib
import asyncio
from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import uvicorn
import shutil
import pypdf

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

# 🧠 NEW FLEXIBLE INTENT RESOLVER MATRIX
def resolve_hardware_intent(user_input: str) -> str | None:
    """Parses natural phrasing variations and normalizes them into strict laptop command mappings"""
    cmd = user_input.lower().strip()
    
    # 1. Console Security & Power Grid Commands
    if any(word in cmd for word in ["lock workstation", "lock pc", "lock computer", "secure pc"]) or cmd == "lock":
        return "lock"
    if any(word in cmd for word in ["go to sleep", "sleep mode", "suspend pc", "pc sleep", "put pc to sleep"]) or cmd == "sleep":
        return "sleep"
        
    # 2. System Performance Monitoring Commands
    if any(word in cmd for word in ["system status", "check status", "pc status", "laptop status", "agent status", "how is my laptop"]):
        return "system status"
        
    # 3. Kernel Level Audio Adjustments
    if any(word in cmd for word in ["volume up", "make louder", "increase volume", "increase sound", "raise volume", "louder"]):
        return "volume up"
    if any(word in cmd for word in ["volume down", "make quieter", "decrease volume", "decrease sound", "lower volume", "quieter", "turn down the sound", "turn down sound"]):
        return "volume down"
    if any(word in cmd for word in ["toggle mute", "silence pc", "unmute", "mute computer", "mute"]):
        return "mute"
    if any(word in cmd for word in ["play media", "pause media", "toggle play", "resume video", "resume music", "play", "pause"]):
        return "play"
        
    # 4. Reverse Visual Capture Controls
    if any(word in cmd for word in ["screenshot", "capture screen", "take snap", "screen snap", "capture display", "take screenshot", "show screen"]):
        return "screenshot"
        
    # 5. Native Application Array Launches
    if "chrome" in cmd or "browser" in cmd:
        if any(word in cmd for word in ["open", "launch", "start", "boot"]): return "open chrome"
    if "notepad" in cmd or "text editor" in cmd:
        if any(word in cmd for word in ["open", "launch", "start"]): return "open notepad"
    if "vscode" in cmd or "vs code" in cmd or "visual studio code" in cmd:
        if any(word in cmd for word in ["open", "launch", "start", "run"]): return "open vscode"
        
    # 6. Web Matrix Target Directives
    if "youtube" in cmd:
        if any(word in cmd for word in ["open", "launch", "start", "watch"]): return "open youtube"
    if "github" in cmd:
        if any(word in cmd for word in ["open", "launch", "start"]): return "open github"
    if "leetcode" in cmd:
        if any(word in cmd for word in ["open", "launch", "start", "solve"]): return "open leetcode"
    if "google" in cmd and not any(word in cmd for word in ["search", "find", "look up"]):
        if any(word in cmd for word in ["open", "launch", "start"]): return "open google"
        
    # 7. Dynamic Web Search Engine Engine Interceptor
    for prefix in ["search for ", "search ", "google ", "look up ", "find "]:
        if cmd.startswith(prefix):
            query_text = cmd.replace(prefix, "", 1).strip()
            if query_text:
                return f"search {query_text}"
                
    return None

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
        for cmd_id, future in list(pending_futures.items()):
            if not future.done():
                future.set_result({"text": "📡 **Hardware Agent Disconnected:** The connection dropped unexpectedly during data transmission.", "image": None})

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
        
        # 📡 UPGRADED INTERCEPTOR GATE: Run flexible natural language verification loop
        hardware_action = resolve_hardware_intent(user_instruction)
        
        if hardware_action:
            if not agent_websocket:
                return {"response": "📡 **Hardware Agent Offline:** Your cloud cluster is active, but your laptop agent is disconnected.", "image": None}
            
            cmd_id = str(asyncio.get_running_loop().time())
            future = asyncio.get_running_loop().create_future()
            pending_futures[cmd_id] = future
            
            try:
                await agent_websocket.send_json({"id": cmd_id, "action": hardware_action})
                result_data = await asyncio.wait_for(future, timeout=10.0)
                
                if isinstance(result_data, dict):
                    return {
                        "response": result_data.get("text", ""),
                        "image": result_data.get("image", None)
                    }
                return {"response": result_data, "image": None}
                
            except asyncio.TimeoutError:
                return {"response": "⚠️ **Transmission Timeout:** Local agent did not reply within the 10-second data window.", "image": None}
            finally:
                pending_futures.pop(cmd_id, None)

        save_message_to_history(sid, title, "user", user_instruction, sender_name)
        chat_context = fetch_session_context(sid, limit=6)
        messages_payload = [{"role": "system", "content": "You are AIRA, an enterprise SaaS dark-aesthetic core assistant."}] + chat_context
        
        env_key = fetch_active_groq_key()
        if not env_key or len(env_key) < 10:
            return {"response": "🔑 **Groq API Key Missing:** Please open the mobile app Sidebar Drawer ➔ System Settings, paste your valid API key, and tap save.", "image": None}

        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {env_key}", "Content-Type": "application/json"}
            api_payload = {"model": "llama-3.1-8b-instant", "messages": messages_payload, "temperature": 0.4}
            async with session.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=api_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    reply = data["choices"][0]["message"]["content"]
                    save_message_to_history(sid, title, "assistant", reply, "AIRA Engine")
                    return {"response": reply, "image": None}
                else:
                    err_text = await response.text()
                    return {"response": f"⚠️ **Groq API Error ({response.status}):** Check if your key is active. Details: {err_text[:100]}", "image": None}
    except Exception as global_error:
        return {"response": f"❌ **Internal Cloud Core Exception:** {str(global_error)}", "image": None}

@app.post("/chat/document")
async def upload_and_analyze_pdf(
    file: UploadFile = File(...),
    session_id: str = Form("default_session"),
    conversation_title: str = Form("Document Analysis Frame"),
    user: str = Form("Anonymous User")
):
    try:
        if not file.filename.lower().endswith('.pdf'):
            return {"response": "❌ **Format Refusal:** AIRA Document Core only parses native `.pdf` files.", "image": None}
        
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        extracted_text = ""
        with open(file_path, "rb") as pdf_file:
            reader = pypdf.PdfReader(pdf_file)
            for page in reader.pages:
                text_content = page.extract_text()
                if text_content:
                    extracted_text += text_content + "\n"
                    
        if not extracted_text.strip():
            return {"response": "⚠️ **Parsing Defect:** The PDF was uploaded but no readable text vector strings could be extracted (it might be a scanned image).", "image": None}
            
        user_display_msg = f"📁 [Uploaded Document File]: {file.filename} ({len(extracted_text)} characters parsed)"
        save_message_to_history(session_id, conversation_title, "user", user_display_msg, user)
        
        env_key = fetch_active_groq_key()
        if not env_key or len(env_key) < 10:
            return {"response": "🔑 **Groq API Key Missing:** Document mapped cleanly, but Groq authorization token is absent.", "image": None}
            
        system_instruction = (
            "You are AIRA, an enterprise SaaS dark-aesthetic core assistant. "
            "The user has uploaded a document file core. Read the full text contents attached below, "
            "and output a beautiful, premium, highly professional summary. Use crisp markdown bullet points, "
            "break it down into executive highlights, and list actionable takeaways tailored for quick mobile viewing."
        )
        
        messages_payload = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Document Name: {file.filename}\n\nDocument Contents:\n{extracted_text}"}
        ]
        
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {env_key}", "Content-Type": "application/json"}
            api_payload = {"model": "llama-3.1-8b-instant", "messages": messages_payload, "temperature": 0.3}
            async with session.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=api_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    analysis_reply = data["choices"][0]["message"]["content"]
                    save_message_to_history(session_id, conversation_title, "assistant", analysis_reply, "AIRA Engine")
                    return {"response": analysis_reply, "image": None}
                else:
                    err_text = await response.text()
                    return {"response": f"⚠️ **Groq API Document Analysis Error ({response.status}):** Details: {err_text[:100]}", "image": None}
                    
    except Exception as doc_error:
        return {"response": f"❌ **Document Pipeline Exception Event:** {str(doc_error)}", "image": None}
    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            try: os.remove(file_path)
            except Exception: pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
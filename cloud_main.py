import os
import json
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
        
        env_key = fetch_active_groq_key()
        if not env_key or len(env_key) < 10:
            return {"response": "🔑 **Groq API Key Missing:** Please open the mobile app Sidebar Drawer ➔ System Settings, paste your valid API key, and tap save.", "image": None}

        save_message_to_history(sid, title, "user", user_instruction, sender_name)
        chat_context = fetch_session_context(sid, limit=6)
        
        system_prompt = (
            "You are AIRA, an advanced enterprise SaaS dark-aesthetic core operating assistant. "
            "You have direct control over the user's physical laptop through specialized hardware tools. "
            "If the user asks you to do something to their computer (like change volume, open apps, take screenshots, lock, sleep), "
            "you MUST invoke the appropriate tool. Be conversational and helpful when answering general questions."
        )
        
        messages_payload = [{"role": "system", "content": system_prompt}] + chat_context
        
        # 🧠 DEFINING THE CHAT COMPLETION TOOLS ARRAY SCHEMA FOR THE LLM LAYER
        tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": "execute_laptop_command",
                    "description": "Call this to execute hardware controls or application launches on the user's physical laptop.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "enum": [
                                    "system status", "lock", "sleep", "screenshot",
                                    "volume up", "volume down", "mute", "play",
                                    "open chrome", "open notepad", "open vscode",
                                    "open youtube", "open github", "open leetcode", "open google"
                                ],
                                "description": "The strict laptop hardware control configuration token."
                            }
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_web_search",
                    "description": "Call this to perform a live Google search query directly inside the laptop's web browser.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The raw text string or topic terms to look up on Google."
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {env_key}", "Content-Type": "application/json"}
            api_payload = {
                "model": "llama-3.1-8b-instant",
                "messages": messages_payload,
                "temperature": 0.2,
                "tools": tools_schema,
                "tool_choice": "auto"
            }
            
            async with session.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=api_payload) as response:
                if response.status != 200:
                    err_text = await response.text()
                    return {"response": f"⚠️ **Groq API Error ({response.status}):** Details: {err_text[:100]}", "image": None}
                
                data = await response.json()
                choice_message = data["choices"][0]["message"]
                
                # 📡 CORE TOOL ROUTING INTERCEPTOR LOOP
                if "tool_calls" in choice_message and choice_message["tool_calls"]:
                    if not agent_websocket:
                        return {"response": "📡 **Hardware Agent Offline:** Your AI brain understood the request, but your physical laptop agent is currently disconnected.", "image": None}
                    
                    tool_call = choice_message["tool_calls"][0]
                    function_name = tool_call["function"]["name"]
                    function_args = json.loads(tool_call["function"]["arguments"])
                    
                    # Map the AI choice to the correct action target
                    hardware_action = ""
                    if function_name == "execute_laptop_command":
                        hardware_action = function_args.get("command", "")
                    elif function_name == "execute_web_search":
                        hardware_action = f"search {function_args.get('query', '')}"
                    
                    if not hardware_action:
                        return {"response": "⚠️ **AI Tool Routing Error:** Failed to parse target operation arguments.", "image": None}
                        
                    cmd_id = str(asyncio.get_running_loop().time())
                    future = asyncio.get_running_loop().create_future()
                    pending_futures[cmd_id] = future
                    
                    try:
                        await agent_websocket.send_json({"id": cmd_id, "action": hardware_action})
                        result_data = await asyncio.wait_for(future, timeout=10.0)
                        
                        if isinstance(result_data, dict):
                            status_text = result_data.get("text", "")
                            save_message_to_history(sid, title, "assistant", status_text, "AIRA Engine")
                            return {
                                "response": status_text,
                                "image": result_data.get("image", None)
                            }
                        save_message_to_history(sid, title, "assistant", result_data, "AIRA Engine")
                        return {"response": result_data, "image": None}
                        
                    except asyncio.TimeoutError:
                        return {"response": "⚠️ **Transmission Timeout:** Local laptop agent did not reply within the data window.", "image": None}
                    finally:
                        pending_futures.pop(cmd_id, None)
                
                # Standard response conversational flow if no tool call was needed
                reply = choice_message.get("content", "")
                save_message_to_history(sid, title, "assistant", reply, "AIRA Engine")
                return {"response": reply, "image": None}
                
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
            return {"response": "⚠️ **Parsing Defect:** The PDF was uploaded but no readable text vector strings could be extracted.", "image": None}
            
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
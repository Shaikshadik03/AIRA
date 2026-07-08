import os
import json
import threading
import webbrowser
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from ddgs import DDGS
from pypdf import PdfReader
import psutil
import pyttsx3

# Import modern asynchronous high-speed web framework modules
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

# Load environment variables from your .env file
load_dotenv()

# Initialize the Groq cloud communication client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Persistent Memory Storage Pointers
MEMORY_FILE = "memory.json"
PROFILE_FILE = "profile.json"
DEADLINES_FILE = "deadlines.json"
EXPENSES_FILE = "expenses.json"

# Initialize FastAPI Web Application Server Registry Node
app = FastAPI(title="AIRA OS Engine Core API", version="1.0.0")

# =====================================================================
# 🔒 SECURE SANDBOX DIRECTORY GUARDRAIL LAYER
# =====================================================================
WORKSPACE_ROOT = os.path.abspath(os.getcwd())

def is_safe_path(target_path: str) -> bool:
    """Verifies if the absolute path resolution stays strictly nested within workspace roots."""
    try:
        absolute_target = os.path.abspath(target_path)
        return absolute_target.startswith(WORKSPACE_ROOT)
    except Exception:
        return False

# =====================================================================
# 🔊 NATIVE VOICE SPEECH SYNTHESIS INITIALIZATION
# =====================================================================
try:
    voice_engine = pyttsx3.init()
    voice_engine.setProperty('rate', 185)
    voices = voice_engine.getProperty('voices')
    if len(voices) > 1:
        voice_engine.setProperty('voice', voices[1].id)
    else:
        voice_engine.setProperty('voice', voices[0].id)
    VOICE_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Voice engine initialization skipped. Headless audio channel default: {e}")
    VOICE_AVAILABLE = False

def aira_speak(text: str):
    """Converts response text tokens into spoken vocal audio outputs safely."""
    if not VOICE_AVAILABLE or not text:
        return
    clean_text = text.replace("<function>", "").replace("</function>", "")
    clean_text = clean_text.replace("<error_message>", "").replace("</error_message>", "")
    try:
        voice_engine.say(clean_text)
        voice_engine.runAndWait()
    except Exception:
        pass

# =====================================================================
# 🚀 AIRA AGENT ACTION TOOL CORES
# =====================================================================

def open_website(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    webbrowser.open(url)
    return f"System message: Successfully opened {url} in Shadik's desktop browser."

def get_current_time() -> str:
    return f"System message: The current local time is {datetime.now().strftime('%I:%M %p')}."

def get_current_date() -> str:
    return f"System message: Today's date is {datetime.now().strftime('%B %d, %Y')}."

def list_files() -> str:
    try:
        files = os.listdir(".")
        if not files:
            return "System message: The current directory workspace folder is empty."
        return f"System message: Active workspace files:\n" + "\n".join([f"- {f}" for f in files])
    except Exception as e:
        return f"System Error: Unable to scan file system: {e}"

def create_file(filename: str, content: str = "") -> str:
    if not is_safe_path(filename):
        return "Security Exception: Blocked attempt to write outside the local repository sandbox."
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"System message: Successfully created file '{filename}' inside sandbox."
    except Exception as e:
        return f"System Error: Failed to create file: {e}"

def create_folder(foldername: str) -> str:
    if not is_safe_path(foldername):
        return "Security Exception: Blocked attempt to create directory targets outside the local sandbox."
    try:
        if os.path.exists(foldername):
            return f"System message: Folder '{foldername}' already exists."
        os.makedirs(foldername, exist_ok=True)
        return f"System message: Successfully created empty folder directory '{foldername}'."
    except Exception as e:
        return f"System Error: Failed to build folder: {e}"

def rename_file(old_name: str, new_name: str) -> str:
    if not is_safe_path(old_name) or not is_safe_path(new_name):
        return "Security Exception: Blocked attempt to mutate path properties outside the sandbox."
    try:
        if not os.path.exists(old_name):
            return f"System Error: '{old_name}' does not exist."
        os.rename(old_name, new_name)
        return f"System message: Successfully renamed '{old_name}' to '{new_name}'."
    except Exception as e:
        return f"System Error: Failed to rename file: {e}"

def delete_file(filename: str) -> str:
    if not is_safe_path(filename):
        return "Security Exception: Deletion request intercepted. Target vector resides outside sandbox scope."
    try:
        if not os.path.exists(filename):
            return f"System Error: File '{filename}' does not exist."
        if os.path.isdir(filename):
            return f"System Error: '{filename}' is a directory folder."
        os.remove(filename)
        return f"System message: Successfully deleted file '{filename}' from local directory."
    except Exception as e:
        return f"System Error: Failed to delete file: {e}"

def read_file(filename: str) -> str:
    if not is_safe_path(filename):
        return "Security Exception: Read target blocked. Vector points outside authenticated sandbox container."
    try:
        if not os.path.exists(filename):
            return f"System Error: Cannot read '{filename}' because it does not exist."
        with open(filename, "r", encoding="utf-8") as f:
            file_data = f.read()
        return f"Workspace File Execution Payload ('{filename}'):\n{file_data}"
    except Exception as e:
        return f"System Error: Failed to read text file contents: {e}"

def read_pdf(file_path: str) -> str:
    if not is_safe_path(file_path):
        return "Security Exception: Blocked attempt to parse document mapping outside sandbox limits."
    try:
        if not os.path.exists(file_path):
            return f"System Error: PDF target document '{file_path}' does not exist."
        reader = PdfReader(file_path)
        text = "".join([page.extract_text() + "\n" for page in reader.pages])
        if not text.strip():
            return "System message: PDF file parsed successfully but contains no readable layout text elements."
        return f"PDF Extraction Content Layer Layout ('{file_path}'):\n{text}"
    except Exception as e:
        return f"System Error: Failed to parse PDF document structures: {e}"

def log_expense(amount: float, category: str, description: str) -> str:
    try:
        ledger = []
        if os.path.exists(EXPENSES_FILE):
            with open(EXPENSES_FILE, "r", encoding="utf-8") as f:
                try: ledger = json.load(f)
                except Exception: ledger = []
        
        transaction = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
            "amount": float(amount),
            "category": category.lower().strip(),
            "description": description.strip()
        }
        ledger.append(transaction)
        
        with open(EXPENSES_FILE, "w", encoding="utf-8") as f:
            json.dump(ledger, f, indent=4)
        return f"System message: Financial ledger updated cleanly! Logged {amount} under '{category}'."
    except Exception as e:
        return f"System Error: Financial data append routine failed: {e}"

def get_financial_report() -> str:
    try:
        if not os.path.exists(EXPENSES_FILE):
            return "System message: Financial data registers are currently empty. No transactions logged."
        with open(EXPENSES_FILE, "r", encoding="utf-8") as f:
            ledger = json.load(f)
        if not ledger:
            return "System message: Financial database sheets contain zero recorded logs."
        
        total_spent = sum([item["amount"] for item in ledger])
        breakdown = {}
        for item in ledger:
            cat = item["category"]
            breakdown[cat] = breakdown.get(cat, 0.0) + item["amount"]
            
        report_text = f"📊 Live Financial Accountability Balance Sheet:\n- Overall Aggregate Spending: {total_spent}\n\nCategory Summaries:\n"
        for category, subtotal in breakdown.items():
            report_text += f"  * {category.title()}: {subtotal}\n"
        return report_text
    except Exception as e:
        return f"System Error: Failed to compute sheet analytics matrices: {e}"

def get_hardware_status() -> str:
    try:
        cpu_load = psutil.cpu_percent(interval=0.1)
        ram_percent = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        battery_str = f"{battery.percent}%" if battery else "N/A"
        return f"System Hardware Report: CPU: {cpu_load}%, RAM: {ram_percent}%, Battery: {battery_str}"
    except Exception as e:
        return f"System Error: Failed to poll telemetry: {e}"

def launch_app(app_name: str) -> str:
    try:
        app_lookup = {
            "notepad": "notepad.exe", "calculator": "calc.exe", "paint": "mspaint.exe",
            "task_manager": "taskmgr.exe", "chrome": "chrome.exe", "vs_code": "code",
            "snipping_tool": "snippingtool.exe", "settings": "ms-settings:",
            "whatsapp": "whatsapp:", "camera": "microsoft.windows.camera:", "clock": "ms-clock:"
        }
        target_name = app_name.lower().strip()
        if "claude" in target_name:
            try:
                os.startfile("claude.exe")
                return "System message: Successfully deployed native Claude desktop application."
            except Exception:
                webbrowser.open("https://claude.ai")
                return "System message: Local shortcut unavailable. Launched Claude AI via browser."
        if target_name in app_lookup:
            os.startfile(app_lookup[target_name])
            return f"System message: Successfully launched application process for '{target_name}'."
        return f"System Error: '{app_name}' is not registered in the safe app profile."
    except Exception as e:
        return f"System Error: Failed to launch system app: {e}"

def kill_app_process(app_name: str) -> str:
    try:
        target = app_name.lower().strip()
        slug_map = {
            "chrome": "chrome.exe", "notepad": "notepad.exe", "calculator": "calc.exe",
            "vscode": "code.exe", "vs code": "code.exe", "paint": "mspaint.exe"
        }
        process_target = slug_map.get(target, target if target.endswith(".exe") else f"{target}.exe")
        
        killed_count = 0
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == process_target.lower():
                    proc.kill()
                    killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        if killed_count > 0:
            return f"System message: Successfully terminated {killed_count} running instance(s) of '{process_target}'."
        return f"System message: Process target execution scan completed. Zero instances of '{process_target}' are running."
    except Exception as e:
        return f"System Error: Process slayer pipeline failed: {e}"

def save_profile_fact(fact_key: str, fact_value: str) -> str:
    try:
        profile = {}
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                try: profile = json.load(f)
                except Exception: profile = {}
        profile[fact_key.lower().strip()] = fact_value.strip()
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=4)
        return f"System message: Long-term fact securely saved: '{fact_key}' = '{fact_value}'."
    except Exception as e:
        return f"System Error: Failed to write to memory: {e}"

def read_profile_facts() -> str:
    try:
        if not os.path.exists(PROFILE_FILE):
            return "System message: Long-term profile memory database is empty."
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            profile = json.load(f)
        if not profile:
            return "System message: Long-term profile memory database is empty."
        return "Long-Term Database Facts:\n" + "\n".join([f"- {k.title()}: {v}" for k, v in profile.items()])
    except Exception as e:
        return f"System Error: Failed to parse long-term registers: {e}"

def add_deadline(event_name: str, target_date: str) -> str:
    try:
        datetime.strptime(target_date.strip(), "%Y-%m-%d")
        deadlines = {}
        if os.path.exists(DEADLINES_FILE):
            with open(DEADLINES_FILE, "r", encoding="utf-8") as f:
                try: deadlines = json.load(f)
                except Exception: deadlines = {}
        deadlines[event_name.strip()] = target_date.strip()
        with open(DEADLINES_FILE, "w", encoding="utf-8") as f:
            json.dump(deadlines, f, indent=4)
        return f"System message: Deadline registered successfully for '{event_name}' on {target_date}."
    except ValueError:
        return "System Error: Invalid layout string format. Target dates must be exactly YYYY-MM-DD."
    except Exception as e:
        return f"System Error: Failed to update scheduler: {e}"

def get_countdown_alerts() -> str:
    try:
        if not os.path.exists(DEADLINES_FILE):
            return "System message: No target deadlines are registered inside the planner profile."
        with open(DEADLINES_FILE, "r", encoding="utf-8") as f:
            deadlines = json.load(f)
        if not deadlines:
            return "System message: No target deadlines are currently tracking."
        today = datetime.now().date()
        countdown_report = ["Live Scheduler Countdown Alerts:"]
        for event, date_str in deadlines.items():
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            days_left = (target_date - today).days
            if days_left > 0:
                countdown_report.append(f"- {event}: {days_left} days remaining (Target: {date_str})")
            elif days_left == 0:
                countdown_report.append(f"- 🔥 {event}: IS HAPPENING TODAY!")
            else:
                countdown_report.append(f"- {event}: Passed {abs(days_left)} days ago ({date_str})")
        return "\n".join(countdown_report)
    except Exception as e:
        return f"System Error: Failed to process timeline array differences: {e}"

def search_internet(query: str) -> str:
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=4)]
            if not results:
                return "System message: Search query returned 0 active text results."
            search_text = "Live Search Engine Indexes Retrieved:\n"
            for r in results:
                search_text += f"Title: {r['title']}\nSnippet: {r['body']}\n\n"
            return search_text
    except Exception as e:
        return f"System Error: Failed to complete internet search: {e}"

def trigger_cloud_integration(endpoint_url: str, payload_json_string: str) -> str:
    try:
        data_packet = json.loads(payload_json_string)
        headers = {"Content-Type": "application/json", "User-Agent": "AIRA-OS-Agent-Core"}
        response = requests.post(endpoint_url, json=data_packet, headers=headers, timeout=8)
        if response.status_code in [200, 201]:
            return f"System message: Cloud Integration successful! Response code: {response.status_code}."
        return f"System message: Cloud server returned status code: {response.status_code}."
    except Exception as e:
        return f"System Error: Cloud integration failed: {e}"


# Scalable Tool Registries Mapping Directories
tool_registry = {
    "open_website": open_website, "get_current_time": get_current_time, "get_current_date": get_current_date,
    "list_files": list_files, "create_file": create_file, "create_folder": create_folder,
    "rename_file": rename_file, "delete_file": delete_file, "read_file": read_file, "read_pdf": read_pdf,
    "log_expense": log_expense, "get_financial_report": get_financial_report,
    "get_hardware_status": get_hardware_status, "launch_app": launch_app, "kill_app_process": kill_app_process,
    "save_profile_fact": save_profile_fact, "read_profile_facts": read_profile_facts, "add_deadline": add_deadline,
    "get_countdown_alerts": get_countdown_alerts, "search_internet": search_internet,
    "trigger_cloud_integration": trigger_cloud_integration
}

# Dynamic Native AI Agent Tool Blueprints Schema Layout Array
aira_tools = [
    {"type": "function", "function": {"name": "open_website", "description": "Opens any web URL in the browser.", "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}}},
    {"type": "function", "function": {"name": "get_current_time", "description": "Returns current local time.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "get_current_date", "description": "Returns current local date.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "list_files", "description": "Lists files in directory.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "create_file", "description": "Creates a new file in local workspace.", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename"]}}},
    {"type": "function", "function": {"name": "create_folder", "description": "Creates folder directory in local workspace.", "parameters": {"type": "object", "properties": {"foldername": {"type": "string"}}, "required": ["foldername"]}}},
    {"type": "function", "function": {"name": "rename_file", "description": "Renames existing file or folder.", "parameters": {"type": "object", "properties": {"old_name": {"type": "string"}, "new_name": {"type": "string"}}, "required": ["old_name", "new_name"]}}},
    {"type": "function", "function": {"name": "delete_file", "description": "Deletes file from directory root completely.", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}}, "required": ["filename"]}}},
    {"type": "function", "function": {"name": "read_file", "description": "Reads text strings stored in target file.", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}}, "required": ["filename"]}}},
    {"type": "function", "function": {"name": "read_pdf", "description": "Extracts text content from a local PDF document file for analysis or summarization.", "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}}},
    {"type": "function", "function": {"name": "log_expense", "description": "Logs an expense entry with a numeric cost value, strict metadata category, and text tracking details.", "parameters": {"type": "object", "properties": {"amount": {"type": "number"}, "category": {"type": "string"}, "description": {"type": "string"}}, "required": ["amount", "category", "description"]}}},
    {"type": "function", "function": {"name": "get_financial_report", "description": "Compiles a tracking summary parsing total outflux calculations and categorical itemized ledgers.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "get_hardware_status", "description": "Pulls machine hardware usage diagnostics.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "launch_app", "description": "Launches local native system application programs.", "parameters": {"type": "object", "properties": {"app_name": {"type": "string"}}, "required": ["app_name"]}}},
    {"type": "function", "function": {"name": "kill_app_process", "description": "Forcefully terminates a running desktop process or application by its name string.", "parameters": {"type": "object", "properties": {"app_name": {"type": "string"}}, "required": ["app_name"]}}},
    {"type": "function", "function": {"name": "save_profile_fact", "description": "Saves fact parameters to user long-term memory file.", "parameters": {"type": "object", "properties": {"fact_key": {"type": "string"}, "fact_value": {"type": "string"}}, "required": ["fact_key", "fact_value"]}}},
    {"type": "function", "function": {"name": "read_profile_facts", "description": "Reads long-term user context profile database facts.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "add_deadline", "description": "Saves an upcoming milestone tracker calendar date.", "parameters": {"type": "object", "properties": {"event_name": {"type": "string"}, "target_date": {"type": "string"}}, "required": ["event_name", "target_date"]}}},
    {"type": "function", "function": {"name": "get_countdown_alerts", "description": "Runs calendar timeline tracking analysis.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "search_internet", "description": "Browses open web index search engines engines dynamically for live data.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "trigger_cloud_integration", "description": "Transmits JSON parameters dynamically to external cloud webhooks.", "parameters": {"type": "object", "properties": {"endpoint_url": {"type": "string"}, "payload_json_string": {"type": "string"}}, "required": ["endpoint_url", "payload_json_string"]}}}
]

def auto_compact_history(history, groq_client):
    if len(history) <= 20:
        return history
    try:
        system_prompt = history[0]
        slice_to_compress = history[1:-4]  
        recent_messages = history[-4:]
        raw_text = ""
        for msg in slice_to_compress:
            content = msg.get("content") or ""
            if msg.get("tool_calls"): content += " [Tool Use Invocations]"
            raw_text += f"{msg.get('role').upper()}: {content}\n"
        compaction_prompt = f"Condense this conversation timeline history entirely into a single narrative paragraph:\n\n{raw_text}"
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": compaction_prompt}]
        )
        return [system_prompt, {"role": "system", "content": f"Summary profile of previous interactions: {response.choices[0].message.content}"}] + recent_messages
    except Exception:
        return history

# Load baseline profile records configuration layouts
loaded_profile_context = ""
if os.path.exists(PROFILE_FILE):
    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        try:
            profile_data = json.load(f)
            if profile_data:
                loaded_profile_context = "\nKnown user profile records:\n" + "\n".join([f"{k.upper()}: {v}" for k, v in profile_data.items()])
        except Exception: pass

# =====================================================================
# 🧠 THE ADAPTIVE SAAS SYSTEM PROMPT CORE
# =====================================================================
DEFAULT_SYSTEM_PROMPT = [{
    "role": "system", 
    "content": (
        "You are AIRA, a professional, highly capable personal AI assistant and custom OS engine built by Shadik. "
        "Respond directly and concisely with adaptive candor and a touch of wit. "
        f"You are running inside a secure sandbox environment on Shadik's multi-platform cloud setup. {loaded_profile_context}\n\n"
        "BALANCED MODE OPERATIONAL RULES:\n"
        "1. Chat completely naturally, casually, and intelligently when answering conversational prompts ('Normal Mode').\n"
        "2. Natively and autonomously invoke your structural tools whenever Shadik asks for concrete actions "
        "(like opening websites, manipulating files, logging finances, checking times, or stopping apps).\n"
        "3. You operate inside an isolated path sandbox server framework. All file systems and ledger operations are tracked.\n"
        "4. Never guess system stats, times, or countdown data. Always call the tool, read the payload, and present the result clearly."
    )
}]

if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        try:
            conversation_history = json.load(f)
            if conversation_history and conversation_history[0]["role"] == "system":
                conversation_history[0] = DEFAULT_SYSTEM_PROMPT[0]
        except Exception: conversation_history = list(DEFAULT_SYSTEM_PROMPT)
else:
    conversation_history = list(DEFAULT_SYSTEM_PROMPT)


def execute_brain_inference(incoming_text: str) -> str:
    """Processes message requests utilizing AIRA's tool-belt schema engine layer."""
    global conversation_history
    conversation_history = auto_compact_history(conversation_history, client)
    conversation_history.append({"role": "user", "content": incoming_text})
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", messages=conversation_history, tools=aira_tools, tool_choice="auto"
        )
        msg = response.choices[0].message
        if msg.tool_calls:
            serialized_calls = []
            for tc in msg.tool_calls:
                serialized_calls.append({"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}})
            conversation_history.append({"role": "assistant", "content": msg.content, "tool_calls": serialized_calls})
            
            for tc in msg.tool_calls:
                name = tc.function.name
                try: args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                except Exception: args = {}
                
                if not isinstance(args, dict): 
                    args = {}
                    
                if name in tool_registry:
                    res = tool_registry[name](**args)
                    conversation_history.append({"role": "tool", "tool_call_id": tc.id, "name": name, "content": res})
            
            final_res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=conversation_history)
            reply = final_res.choices[0].message.content
        else:
            reply = msg.content
        if reply:
            conversation_history.append({"role": "assistant", "content": reply})
            return reply
        return "AIRA Core: Processed successfully."
    except Exception as e:
        return f"AIRA System Exception Core Error: {e}"

def running_multiplatform_listener_loop():
    """Asynchronous background server daemon thread scanning cloud vectors for mobile inputs."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        print("🪐 [Level 16 Server Engine] Telegram Node Standby: Token not set.")
        return
        
    print("🚀 [Level 16 Server Engine] Listening to Mobile Cloud Bot Vectors...")
    base_url = f"https://api.telegram.org/bot{bot_token}"
    last_update_id = 0
    
    while True:
        try:
            url = f"{base_url}/getUpdates?offset={last_update_id + 1}&timeout=5"
            resp = requests.get(url, timeout=10).json()
            if "result" in resp:
                for update in resp["result"]:
                    last_update_id = update["update_id"]
                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        user_msg = update["message"]["text"]
                        print(f"📲 Incoming Wireless Data Frame: '{user_msg}'")
                        
                        aira_reply = execute_brain_inference(user_msg)
                        
                        send_url = f"{base_url}/sendMessage"
                        requests.post(send_url, json={"chat_id": chat_id, "text": aira_reply}, timeout=5)
        except Exception:
            pass
        time.sleep(1)

# =====================================================================
# 🌐 FASTAPI PRODUCTION SERVER ENDPOINTS INTERFACE
# =====================================================================

@app.get("/")
async def serve_root_api_healthcheck():
    """Returns a high-speed system metrics dictionary log payload tracking server state."""
    return {
        "status": "online",
        "engine": "AIRA OS SaaS Agent Core",
        "timestamp": datetime.now().isoformat(),
        "sandbox_root": WORKSPACE_ROOT,
        "telemetry": {
            "cpu_utilization_percent": psutil.cpu_percent(),
            "memory_utilization_percent": psutil.virtual_memory().percent
        }
    }

@app.post("/chat")
async def serve_inference_endpoint(request: Request):
    """Secure inbound programmatic routing connector handling JSON payload message strings."""
    try:
        body = await request.json()
        user_message = body.get("message", "").strip()
        if not user_message:
            raise HTTPException(status_code=400, detail="Payload execution request missing required 'message' key parameter.")
        
        agent_reply = execute_brain_inference(user_message)
        return {"sender": "AIRA", "response": agent_reply, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Internal API Server Exception: {e}"})

if __name__ == "__main__":
    # Start the persistent Telegram mobile synchronization node in a separate daemon process thread
    threading.Thread(target=running_multiplatform_listener_loop, daemon=True).start()
    
    # Run the high-speed local HTTP server interface block
    import uvicorn
    print("⚡ Starting Local Production Server Stack Engine on Port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
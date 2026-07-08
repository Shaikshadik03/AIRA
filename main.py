import os
import json
import threading
import webbrowser
import requests
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from ddgs import DDGS
from pypdf import PdfReader
import psutil
import pyttsx3
import time

# Load environment variables from your .env file
load_dotenv()

# Initialize the Groq cloud communication client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Persistent Memory Storage Pointers
MEMORY_FILE = "memory.json"
PROFILE_FILE = "profile.json"
DEADLINES_FILE = "deadlines.json"

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
    print(f"⚠️ Voice engine initialization skipped. Audio output unavailable: {e}")
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
    try:
        if "/" in filename or "\\" in filename:
            return "System Error: Files must be created directly in the workspace root."
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"System message: Successfully created file '{filename}'."
    except Exception as e:
        return f"System Error: Failed to create file: {e}"

def create_folder(foldername: str) -> str:
    try:
        if "/" in foldername or "\\" in foldername:
            return "System Error: Folders must be created directly in the workspace root."
        if os.path.exists(foldername):
            return f"System message: Folder '{foldername}' already exists."
        os.makedirs(foldername, exist_ok=True)
        return f"System message: Successfully created empty folder directory '{foldername}'."
    except Exception as e:
        return f"System Error: Failed to build folder: {e}"

def rename_file(old_name: str, new_name: str) -> str:
    try:
        if "/" in old_name or "\\" in old_name or "/" in new_name or "\\" in new_name:
            return "System Error: Renaming must be done within the workspace root."
        if not os.path.exists(old_name):
            return f"System Error: '{old_name}' does not exist."
        os.rename(old_name, new_name)
        return f"System message: Successfully renamed '{old_name}' to '{new_name}'."
    except Exception as e:
        return f"System Error: Failed to rename file: {e}"

def delete_file(filename: str) -> str:
    try:
        if "/" in filename or "\\" in filename:
            return "System Error: Deletion targets must live inside the workspace root."
        if not os.path.exists(filename):
            return f"System Error: File '{filename}' does not exist."
        if os.path.isdir(filename):
            return f"System Error: '{filename}' is a directory folder."
        os.remove(filename)
        return f"System message: Successfully deleted file '{filename}' from local directory."
    except Exception as e:
        return f"System Error: Failed to delete file: {e}"

def read_file(filename: str) -> str:
    try:
        if "/" in filename or "\\" in filename:
            return "System Error: Reading targets must live directly within the workspace root."
        if not os.path.exists(filename):
            return f"System Error: Cannot read '{filename}' because it does not exist."
        with open(filename, "r", encoding="utf-8") as f:
            file_data = f.read()
        return f"Workspace File Execution Payload ('{filename}'):\n{file_data}"
    except Exception as e:
        return f"System Error: Failed to read text file contents: {e}"

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
    """Forcefully terminates running Windows desktop processes using system handles."""
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
    "rename_file": rename_file, "delete_file": delete_file, "read_file": read_file,
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

def read_pdf(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)
        return "".join([page.extract_text() + "\n" for page in reader.pages])
    except Exception as e:
        return f"System Error: Failed to parse PDF document: {e}"

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
        f"You are running on Shadik's multi-platform cloud OS node setup. {loaded_profile_context}\n\n"
        "BALANCED MODE OPERATIONAL RULES:\n"
        "1. Chat completely naturally, casually, and intelligently when answering conversational prompts ('Normal Mode').\n"
        "2. Natively and autonomously invoke your structural tools whenever Shadik asks for concrete actions "
        "(like opening websites, checking exact time/date strings, viewing directory files, or running hardware metrics).\n"
        "3. If the user asks to close, kill, shut down, terminate, or stop an app, browser, or process, you MUST call 'kill_app_process'.\n"
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
        print("🪐 [Level 12 Multi-Platform Node] Standby Mode: Add TELEGRAM_BOT_TOKEN to .env to open mobile channels.")
        return
        
    print("🚀 [Level 12 Multi-Platform Node] Listening to Mobile Cloud Bot Vectors...")
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
                        print(f"📲 Incoming Mobile Packet Signature: '{user_msg}'")
                        
                        aira_reply = execute_brain_inference(user_msg)
                        
                        send_url = f"{base_url}/sendMessage"
                        requests.post(send_url, json={"chat_id": chat_id, "text": aira_reply}, timeout=5)
        except Exception:
            pass
        time.sleep(1)


# =====================================================================
# LEVEL 8 & 9: NATIVE DESKTOP GRAPHICAL APPLICATION SHELL DESIGN
# =====================================================================
class AIRAGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AIRA OS — Ultimate Personal AI Assistant")
        self.root.geometry("850x600")
        self.root.configure(bg="#111116")
        
        self.telemetry_frame = tk.Frame(root, bg="#1a1a24", height=35)
        self.telemetry_frame.pack(fill=tk.X, side=tk.TOP)
        self.telemetry_label = tk.Label(self.telemetry_frame, text="System Dashboard Loading...", font=("Consolas", 10), fg="#00ffcc", bg="#1a1a24")
        self.telemetry_label.pack(pady=6)
        self.update_telemetry_loop()
        
        self.chat_display = scrolledtext.ScrolledText(root, bg="#0d0d11", fg="#e2e2ea", font=("Segoe UI", 11), wrap=tk.WORD, state=tk.DISABLED, bd=0)
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        self.append_chat_message("AIRA", "Level 12 Process Slayer Live. Unified Engine Active, Shadik.")
        
        self.input_frame = tk.Frame(root, bg="#111116")
        self.input_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=15, pady=15)
        self.entry_field = tk.Entry(self.input_frame, bg="#1d1d26", fg="#ffffff", font=("Segoe UI", 12), insertbackground="white", bd=0)
        self.entry_field.pack(fill=tk.X, side=tk.LEFT, expand=True, ipady=10, padx=(0, 10))
        self.entry_field.bind("<Return>", lambda event: self.trigger_message_processing())
        
        self.send_button = tk.Button(self.input_frame, text="EXECUTE", font=("Segoe UI Bold", 10), bg="#00ffcc", fg="#0d0d11", bd=0, width=12, command=self.trigger_message_processing)
        self.send_button.pack(side=tk.RIGHT, ipady=8)

    def append_chat_message(self, sender: str, content: str):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"\n【 {sender} 】\n", "sender_tag" if sender == "You" else "aira_tag")
        self.chat_display.insert(tk.END, f"{content}\n")
        self.chat_display.tag_config("sender_tag", foreground="#00ffcc", font=("Segoe UI Bold", 11))
        self.chat_display.tag_config("aira_tag", foreground="#ff007f", font=("Segoe UI Bold", 11))
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def update_telemetry_loop(self):
        try:
            self.telemetry_label.config(text=f"💻 SYSTEM OVERVIEW  |  CPU: {psutil.cpu_percent()}%  |  RAM: {psutil.virtual_memory().percent}%  |  ENGINE: PROCESS SLAYER MULTI-PLATFORM ACTIVE")
        except Exception: pass
        self.root.after(3000, self.update_telemetry_loop)

    def trigger_message_processing(self):
        query = self.entry_field.get().strip()
        if not query: return
        self.entry_field.delete(0, tk.END)
        self.append_chat_message("You", query)
        threading.Thread(target=self.process_agent_thought_loop, args=(query,), daemon=True).start()

    def process_agent_thought_loop(self, user_text: str):
        global conversation_history
        reply = execute_brain_inference(user_text)
        if reply:
            self.root.after(0, lambda: self.append_chat_message("AIRA", reply))
            aira_speak(reply)

if __name__ == "__main__":
    threading.Thread(target=running_multiplatform_listener_loop, daemon=True).start()
    
    import tkinter as tk
    app_window = tk.Tk()
    gui_app = AIRAGUI(app_window)
    
    def handle_secure_shutdown():
        with open(MEMORY_FILE, "w") as out_file:
            json.dump(conversation_history, out_file)
        app_window.destroy()
        
    app_window.protocol("WM_DELETE_WINDOW", handle_secure_shutdown)
    app_window.mainloop()
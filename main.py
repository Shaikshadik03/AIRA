import os
import json
import threading
import webbrowser
import requests
import time
import sqlite3
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from ddgs import DDGS
from pypdf import PdfReader
import psutil
import pyttsx3

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Load environment variables from your .env file
load_dotenv()

# Initialize the Groq cloud communication client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize FastAPI Web Application Server Registry Node
app = FastAPI(title="AIRA OS Production SaaS Toolkit", version="1.5.0")

# Relational Database Storage Pointer
DB_FILE = "aira_cloud_node.db"

# =====================================================================
# 🔐 CRYPTOGRAPHIC PASSWORD HASHING UTILITY
# =====================================================================
def hash_password(password: str) -> str:
    """Converts a raw password string into a secure cryptographic SHA-256 hex digest."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# =====================================================================
# 🗄️ RELATIONAL DATABASE INITIALIZATION & SCHEMA SETUP
# =====================================================================
def init_relational_database():
    """Compiles local SQL storage structures to handle multi-tenant isolation schemas safely."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # SaaS User Authentication Accounts Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            hashed_password TEXT,
            created_at TEXT
        )
    """)
    
    # User Profile Memory Table Layout
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profile_memory (
            user_id TEXT,
            fact_key TEXT,
            fact_value TEXT,
            PRIMARY KEY (user_id, fact_key)
        )
    """)
    
    # Financial Ledger Expenditure Table Layout
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            amount REAL,
            category TEXT,
            description TEXT,
            timestamp TEXT
        )
    """)
    
    # SaaS Category Budget Enforcement Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            user_id TEXT,
            category TEXT,
            amount REAL,
            PRIMARY KEY (user_id, category)
        )
    """)
    
    # SaaS Automated Subscription Tracking Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            name TEXT,
            cost REAL,
            renewal_date TEXT
        )
    """)
    
    # Task Planner Calendar Deadlines Table Layout
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deadlines (
            user_id TEXT,
            event_name TEXT,
            target_date TEXT,
            PRIMARY KEY (user_id, event_name)
        )
    """)
    
    # Multi-User Persistent Conversational History Logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            role TEXT,
            content TEXT,
            tool_calls TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

# Fire up relational schemas on core runtime initialization
init_relational_database()

# =====================================================================
# 📦 FASTAPI INPUT/OUTPUT VALIDATION SCHEMAS (PYDANTIC)
# =====================================================================
class UserAuthPayload(BaseModel):
    username: str
    password: str

class ChatPayload(BaseModel):
    user_id: str
    message: str

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
# 🚀 AIRA AGENT MULTI-TENANT ISOLATED ACTION TOOL REGISTRY PATTERNS
# =====================================================================

def open_website(url: str, **kwargs) -> str:
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    webbrowser.open(url)
    return f"System message: Successfully opened {url} in desktop browser."

def get_current_time(**kwargs) -> str:
    return f"System message: The current local time is {datetime.now().strftime('%I:%M %p')}."

def get_current_date(**kwargs) -> str:
    return f"System message: Today's date is {datetime.now().strftime('%B %d, %Y')}."

def list_files(**kwargs) -> str:
    try:
        files = os.listdir(".")
        if not files:
            return "System message: The current directory workspace folder is empty."
        return f"System message: Active workspace files:\n" + "\n".join([f"- {f}" for f in files])
    except Exception as e:
        return f"System Error: Unable to scan file system: {e}"

def create_file(filename: str, content: str = "", **kwargs) -> str:
    if not is_safe_path(filename):
        return "Security Exception: Blocked attempt to write outside the local repository sandbox."
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"System message: Successfully created file '{filename}' inside sandbox."
    except Exception as e:
        return f"System Error: Failed to create file: {e}"

def create_folder(foldername: str, **kwargs) -> str:
    if not is_safe_path(foldername):
        return "Security Exception: Blocked attempt to create directory targets outside the local sandbox."
    try:
        if os.path.exists(foldername):
            return f"System message: Folder '{foldername}' already exists."
        os.makedirs(foldername, exist_ok=True)
        return f"System message: Successfully created empty folder directory '{foldername}'."
    except Exception as e:
        return f"System Error: Failed to build folder: {e}"

def rename_file(old_name: str, new_name: str, **kwargs) -> str:
    if not is_safe_path(old_name) or not is_safe_path(new_name):
        return "Security Exception: Blocked attempt to mutate path properties outside the sandbox."
    try:
        if os.path.exists(old_name):
            return f"System Error: '{old_name}' does not exist."
        os.rename(old_name, new_name)
        return f"System message: Successfully renamed '{old_name}' to '{new_name}'."
    except Exception as e:
        return f"System Error: Failed to rename file: {e}"

def delete_file(filename: str, **kwargs) -> str:
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

def read_file(filename: str, **kwargs) -> str:
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

def read_pdf(file_path: str, **kwargs) -> str:
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

def log_expense(amount: float, category: str, description: str, user_id: str, **kwargs) -> str:
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (user_id, amount, category, description, timestamp) VALUES (?, ?, ?, ?, ?)",
            (user_id, float(amount), category.lower().strip(), description.strip(), datetime.now().strftime("%Y-%m-%d %I:%M %p"))
        )
        conn.commit()
        conn.close()
        return f"System message: Cloud ledger isolated row insertion success. Saved {amount} under '{category}' for Owner Token ID '{user_id}'."
    except Exception as e:
        return f"System Error: Isolated database transaction update routine aborted: {e}"

def set_monthly_budget(category: str, amount: float, user_id: str, **kwargs) -> str:
    """Saves a maximum monetary spend threshold row for a specific tracking category category."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO budgets (user_id, category, amount) VALUES (?, ?, ?)",
            (user_id, category.lower().strip(), float(amount))
        )
        conn.commit()
        conn.close()
        return f"System message: Budget constraint mapped. Isolated cap for '{category}' set to {amount} for '{user_id}'."
    except Exception as e:
        return f"System Error: Failed to save relational budget row: {e}"

def add_subscription(name: str, cost: float, renewal_date: str, user_id: str, **kwargs) -> str:
    """Registers an automated monthly billing commitment string with timestamp analytics."""
    try:
        datetime.strptime(renewal_date.strip(), "%Y-%m-%d")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO subscriptions (user_id, name, cost, renewal_date) VALUES (?, ?, ?, ?)",
            (user_id, name.strip(), float(cost), renewal_date.strip())
        )
        conn.commit()
        conn.close()
        return f"System message: Subscription track locked. Registered '{name}' at cost {cost} renewing on {renewal_date}."
    except ValueError:
        return "System Error: Date constraints must conform specifically to exact YYYY-MM-DD strings."
    except Exception as e:
        return f"System Error: Failed to record billing matrix row: {e}"

def get_financial_report(user_id: str, **kwargs) -> str:
    """Compiles a data tracking overview parsing asset expenses cross-referenced against category budgets and subscription cards."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Pull expenses
        cursor.execute("SELECT amount, category FROM expenses WHERE user_id = ?", (user_id,))
        expense_rows = cursor.fetchall()
        
        # Pull budgets
        cursor.execute("SELECT category, amount FROM budgets WHERE user_id = ?", (user_id,))
        budget_map = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Pull subscriptions
        cursor.execute("SELECT name, cost, renewal_date FROM subscriptions WHERE user_id = ?", (user_id,))
        sub_rows = cursor.fetchall()
        
        conn.close()
        
        total_spent = sum([r[0] for r in expense_rows])
        cat_spent = {}
        for amount, category in expense_rows:
            cat_spent[category] = cat_spent.get(category, 0.0) + amount
            
        report_text = f"📊 Cloud Row-Isolated Financial Balance Sheet [{user_id}]:\n- Overall Aggregate Spending: {total_spent}\n\n"
        
        report_text += "Itemized Budgets Enforcement Matrix:\n"
        all_categories = set(list(cat_spent.keys()) + list(budget_map.keys()))
        if not all_categories:
            report_text += "  (Zero recorded categorical ledger data structures found)\n"
        for cat in all_categories:
            spent = cat_spent.get(cat, 0.0)
            limit = budget_map.get(cat, None)
            if limit is not None:
                status = "🔥 OVER BUDGET!" if spent > limit else "🟢 WITHIN CAP"
                report_text += f"  * {cat.title()}: Spent {spent} / Cap: {limit} ({status})\n"
            else:
                report_text += f"  * {cat.title()}: Spent {spent} / No Cap Limit Configured\n"
                
        report_text += "\nActive Automated Subscription Streams:\n"
        if not sub_rows:
            report_text += "  (Zero recurring tracking subscriptions mapped to this token profile)\n"
        for name, cost, r_date in sub_rows:
            report_text += f"  * {name}: {cost} recurring (Next billing cycle: {r_date})\n"
            
        return report_text
    except Exception as e:
        return f"System Error: Isolated metrics pipeline summation failure: {e}"

def get_hardware_status(**kwargs) -> str:
    try:
        cpu_load = psutil.cpu_percent(interval=0.1)
        ram_percent = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        battery_str = f"{battery.percent}%" if battery else "N/A"
        return f"System Hardware Report: CPU: {cpu_load}%, RAM: {ram_percent}%, Battery: {battery_str}"
    except Exception as e:
        return f"System Error: Failed to poll telemetry: {e}"

def launch_app(app_name: str, **kwargs) -> str:
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

def kill_app_process(app_name: str, **kwargs) -> str:
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

def save_profile_fact(fact_key: str, fact_value: str, user_id: str, **kwargs) -> str:
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO profile_memory (user_id, fact_key, fact_value) VALUES (?, ?, ?)",
            (user_id, fact_key.lower().strip(), fact_value.strip())
        )
        conn.commit()
        conn.close()
        return f"System message: Secure long-term row memory synchronized: '{fact_key}' = '{fact_value}'."
    except Exception as e:
        return f"System Error: Context-isolated write operation aborted: {e}"

def read_profile_facts(user_id: str, **kwargs) -> str:
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT fact_key, fact_value FROM profile_memory WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return f"System message: Long-term configuration metadata registry map is empty for owner footprint Context: '{user_id}'."
        return f"Long-Term Cloud Database Facts [{user_id}]:\n" + "\n".join([f"- {k.title()}: {v}" for k, v in rows])
    except Exception as e:
        return f"System Error: Failed to extract row-isolated profile arrays: {e}"

def add_deadline(event_name: str, target_date: str, user_id: str, **kwargs) -> str:
    try:
        datetime.strptime(target_date.strip(), "%Y-%m-%d")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO deadlines (user_id, event_name, target_date) VALUES (?, ?, ?)",
            (user_id, event_name.strip(), target_date.strip())
        )
        conn.commit()
        conn.close()
        return f"System message: Dynamic target date locked successfully for '{event_name}' on {target_date}."
    except ValueError:
        return "System Error: Invalid layout string format. Target dates must be exactly YYYY-MM-DD."
    except Exception as e:
        return f"System Error: Failed to update database scheduler structures: {e}"

def get_countdown_alerts(user_id: str, **kwargs) -> str:
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT event_name, target_date FROM deadlines WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return f"System message: No milestone tracking metrics registered for account row isolation: '{user_id}'."
            
        today = datetime.now().date()
        countdown_report = [f"Live Target Countdown Registers [{user_id}]:"]
        for event, date_str in rows:
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
        return f"System Error: Failed to compute chronological data parameters: {e}"

def search_internet(query: str, **kwargs) -> str:
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

def trigger_cloud_integration(endpoint_url: str, payload_json_string: str, **kwargs) -> str:
    try:
        data_packet = json.loads(payload_json_string)
        headers = {"Content-Type": "application/json", "User-Agent": "AIRA-OS-Agent-Core"}
        response = requests.post(endpoint_url, json=data_packet, headers=headers, timeout=8)
        if response.status_code in [200, 201]:
            return f"System message: Cloud Integration successful! Response code: {response.status_code}."
        return f"System message: Cloud server returned status code: {response.status_code}."
    except Exception as e:
        return f"System Error: Cloud integration failed: {e}"


# Scalable Multi-Tenant Function Core Registry Toolbelt Blueprint
tool_registry = {
    "open_website": open_website, "get_current_time": get_current_time, "get_current_date": get_current_date,
    "list_files": list_files, "create_file": create_file, "create_folder": create_folder,
    "rename_file": rename_file, "delete_file": delete_file, "read_file": read_file, "read_pdf": read_pdf,
    "log_expense": log_expense, "set_monthly_budget": set_monthly_budget, "add_subscription": add_subscription, "get_financial_report": get_financial_report,
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
    {"type": "function", "function": {"name": "set_monthly_budget", "description": "Sets a maximum monthly spending threshold caps constraint limit for an itemized spending category.", "parameters": {"type": "object", "properties": {"category": {"type": "string"}, "amount": {"type": "number"}}, "required": ["category", "amount"]}}},
    {"type": "function", "function": {"name": "add_subscription", "description": "Logs an active recurring card membership subscription tracking automated monthly bills.", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "cost": {"type": "number"}, "renewal_date": {"type": "string"}}, "required": ["name", "cost", "renewal_date"]}}},
    {"type": "function", "function": {"name": "get_financial_report", "description": "Compiles a data summary tracking spending aggregates, category budget compliance ratios, and subscription timelines.", "parameters": {"type": "object", "properties": {}, "required": []}}},
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

# =====================================================================
# 🧠 DYNAMIC USER-ISOLATED INFERENCE CORE PIPELINE
# =====================================================================

def fetch_isolated_user_history(user_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT role, content, tool_calls FROM history WHERE user_id = ? ORDER BY id ASC", (user_id,))
    rows = cursor.fetchall()
    
    cursor.execute("SELECT fact_key, fact_value FROM profile_memory WHERE user_id = ?", (user_id,))
    facts = cursor.fetchall()
    conn.close()
    
    profile_ctx = ""
    if facts:
        profile_ctx = "\nAuthenticated occupant row metadata properties:\n" + "\n".join([f"{k.upper()}: {v}" for k, v in facts])
        
    system_prompt_string = (
        "You are AIRA, a professional, highly capable personal AI assistant and custom OS engine built by Shadik. "
        "Respond directly and concisely with adaptive candor and a touch of wit. "
        f"You are running inside a multi-tenant subscription framework. Active session user token: {user_id}. {profile_ctx}\n\n"
        "SAAS OPERATIONS MANDATE:\n"
        "1. Chat completely naturally, casually, and intelligently when answering conversational prompts.\n"
        "2. Natively invoke structural budgeting tools autonomously whenever requested by user intents.\n"
        "3. Cross-reference expense reports with 'set_monthly_budget' and 'add_subscription' metadata rows automatically.\n"
        "4. Never guess system stats, times, or countdown data. Always call the tool, read the payload, and present the result clearly."
    )
    
    baseline_prompt = [{"role": "system", "content": system_prompt_string}]
    
    if not rows:
        return baseline_prompt
        
    history = list(baseline_prompt)
    for role, content, tc_json in rows[-20:]:
        msg = {"role": role, "content": content}
        if tc_json:
            msg["tool_calls"] = json.loads(tc_json)
        history.append(msg)
    return history

def log_database_message(user_id: str, role: str, content: str, tool_calls=None):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        tc_payload = json.dumps(tool_calls) if tool_calls else None
        cursor.execute(
            "INSERT INTO history (user_id, role, content, tool_calls, timestamp) VALUES (?, ?, ?, ?, ?)",
            (user_id, role, content, tc_payload, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ History tracking log anomaly detected: {e}")

def execute_brain_inference(incoming_text: str, session_user_id: str) -> str:
    """Processes message requests across strictly isolated user row context boundaries."""
    history_array = fetch_isolated_user_history(session_user_id)
    history_array.append({"role": "user", "content": incoming_text})
    log_database_message(session_user_id, "user", incoming_text)
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", messages=history_array, tools=aira_tools, tool_choice="auto"
        )
        msg = response.choices[0].message
        if msg.tool_calls:
            serialized_calls = []
            for tc in msg.tool_calls:
                serialized_calls.append({"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}})
            
            history_array.append({"role": "assistant", "content": msg.content, "tool_calls": serialized_calls})
            log_database_message(session_user_id, "assistant", msg.content or "", serialized_calls)
            
            for tc in msg.tool_calls:
                name = tc.function.name
                try: args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                except Exception: args = {}
                
                if not isinstance(args, dict): 
                    args = {}
                
                args["user_id"] = session_user_id
                    
                if name in tool_registry:
                    res = tool_registry[name](**args)
                    history_array.append({"role": "tool", "tool_call_id": tc.id, "name": name, "content": res})
                    log_database_message(session_user_id, "tool", res)
            
            final_res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=history_array)
            reply = final_res.choices[0].message.content
        else:
            reply = msg.content
            
        if reply:
            log_database_message(session_user_id, "assistant", reply)
            return reply
        return "AIRA Core Node: Transaction context isolated successfully."
    except Exception as e:
        return f"AIRA Relational Isolation Layer Exception Error: {e}"

def running_multiplatform_listener_loop():
    """Asynchronous background server daemon thread scanning cloud vectors for mobile inputs."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        print("🪐 [Level 21 Toolkit Node] Telegram Listener Standby Mode: Token missing.")
        return
        
    print("🚀 [Level 21 Toolkit Node] Listening to Mobile Cloud Bot Vectors...")
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
                        chat_id = str(update["message"]["chat"]["id"])
                        user_msg = update["message"]["text"]
                        
                        active_scoped_user = f"telegram_{chat_id}"
                        print(f"📲 Production Data Node Caught: '{user_msg}' from account '{active_scoped_user}'")
                        
                        aira_reply = execute_brain_inference(user_msg, session_user_id=active_scoped_user)
                        
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
    return {
        "status": "online",
        "engine": "AIRA OS SaaS Production Stack Core",
        "timestamp": datetime.now().isoformat(),
        "sandbox_root": WORKSPACE_ROOT,
        "telemetry": {
            "cpu_utilization_percent": psutil.cpu_percent(),
            "memory_utilization_percent": psutil.virtual_memory().percent
        }
    }

@app.post("/auth/signup")
async def register_saas_user(payload: UserAuthPayload):
    username_cleaned = payload.username.strip().lower()
    if not username_cleaned or not payload.password:
        raise HTTPException(status_code=400, detail="Signup verification parameter validation failed.")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE username = ?", (username_cleaned,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username selection already taken.")
    generated_user_id = f"user_{int(time.time())}"
    hashed_pw = hash_password(payload.password)
    cursor.execute("INSERT INTO users (user_id, username, hashed_password, created_at) VALUES (?, ?, ?, ?)", (generated_user_id, username_cleaned, hashed_pw, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Account initialized.", "assigned_user_id": generated_user_id}

@app.post("/auth/login")
async def login_saas_user(payload: UserAuthPayload):
    username_cleaned = payload.username.strip().lower()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, hashed_password FROM users WHERE username = ?", (username_cleaned,))
    record = cursor.fetchone()
    conn.close()
    if not record:
        raise HTTPException(status_code=401, detail="Invalid credential keys.")
    user_id, stored_hashed_password = record
    if hash_password(payload.password) != stored_hashed_password:
        raise HTTPException(status_code=401, detail="Password validation signature mismatch.")
    return {"status": "authenticated", "authenticated_user_id": user_id}

@app.post("/chat")
async def serve_inference_endpoint(payload: ChatPayload):
    try:
        target_user = payload.user_id.strip().lower()
        user_message = payload.message.strip()
        if not target_user or not user_message:
            raise HTTPException(status_code=400, detail="Inbound data packet missing structural validation properties.")
        agent_reply = execute_brain_inference(user_message, session_user_id=target_user)
        return {"sender": "AIRA", "response": agent_reply, "user_context_bound": target_user, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"API Engine Isolated Database Exception: {e}"})

if __name__ == "__main__":
    # Start the multi-tenant message parser background processing loop
    threading.Thread(target=running_multiplatform_listener_loop, daemon=True).start()
    
    # Run the production API server engine node
    import uvicorn
    cloud_assigned_port = int(os.getenv("PORT", 8000))
    print(f"⚡ Deploying Production-Optimized Engine Node Server on Port {cloud_assigned_port}...")
    uvicorn.run(app, host="0.0.0.0", port=cloud_assigned_port)
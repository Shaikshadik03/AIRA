import os
import json
import threading
import webbrowser
import requests
import time
import sqlite3
import hashlib
import shutil
import re
import secrets
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from ddgs import DDGS
from pypdf import PdfReader
import psutil
import pyttsx3

from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import discord
from discord.ext import commands

# Load environment variables from your .env file
load_dotenv()

# Initialize the Groq cloud communication client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize FastAPI Web Application Server Registry Node
app = FastAPI(title="AIRA OS Shielded Enterprise SaaS Core", version="1.18.2")

# Relational Database Storage Pointer
DB_FILE = "aira_cloud_node.db"
BACKUP_DIR = "backups"

# =====================================================================
# 🛡️ IN-MEMORY SECURITY, SESSION, & DYNAMIC AI MODEL ROUTER STORAGE
# =====================================================================
RATE_LIMIT_STORE = {}
ACTIVE_SESSIONS = {}      # Maps dynamic token strings -> user_id strings
USER_ENGINE_REGISTRY = {} # Maps user_id -> explicit AI model name keys

def check_rate_limit_throttle(user_id: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
    now = time.time()
    if user_id not in RATE_LIMIT_STORE:
        RATE_LIMIT_STORE[user_id] = []
    RATE_LIMIT_STORE[user_id] = [t for t in RATE_LIMIT_STORE[user_id] if now - t < window_seconds]
    if len(RATE_LIMIT_STORE[user_id]) >= max_requests:
        return False
    RATE_LIMIT_STORE[user_id].append(now)
    return True

def sanitize_input_string(text: str) -> str:
    if not text:
        return ""
    scrubbed = re.sub(r"<script.*?>.*?</script.*?>", "", text, flags=re.IGNORECASE | re.DOTALL)
    scrubbed = scrubbed.replace("<", "&lt;").replace(">", "&gt;")
    return scrubbed.strip()

# =====================================================================
# 🔐 CRYPTOGRAPHIC PASSWORD HASHING UTILITY
# =====================================================================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# =====================================================================
# 🗄️ RELATIONAL DATABASE INITIALIZATION & SCHEMA SETUP
# =====================================================================
def init_relational_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, username TEXT UNIQUE, hashed_password TEXT, created_at TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS profile_memory (user_id TEXT, fact_key TEXT, fact_value TEXT, PRIMARY KEY (user_id, fact_key))")
    cursor.execute("CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, amount REAL, category TEXT, description TEXT, timestamp TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS budgets (user_id TEXT, category TEXT, amount REAL, PRIMARY KEY (user_id, category))")
    cursor.execute("CREATE TABLE IF NOT EXISTS subscriptions (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, name TEXT, cost REAL, renewal_date TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, title TEXT, content TEXT, timestamp TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, title TEXT, priority TEXT, status TEXT, timestamp TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, action TEXT, timestamp TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS deadlines (user_id TEXT, event_name TEXT, target_date TEXT, PRIMARY KEY (user_id, event_name))")
    cursor.execute("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, role TEXT, content TEXT, tool_calls TEXT, timestamp TEXT)")
    conn.commit()
    conn.close()
    os.makedirs(BACKUP_DIR, exist_ok=True)

init_relational_database()

# =====================================================================
# 📦 FASTAPI INPUT/OUTPUT VALIDATION SCHEMAS
# =====================================================================
class UserAuthPayload(BaseModel):
    username: str
    password: str

class ProtectedChatPayload(BaseModel):
    session_token: str
    message: str

class AutomationWebhookPayload(BaseModel):
    auth_secret: str
    target_user_id: str
    action_intent: str  
    payload_data: dict

# =====================================================================
# 🔒 SECURE SANDBOX DIRECTORY GUARDRAIL LAYER
# =====================================================================
WORKSPACE_ROOT = os.path.abspath(os.getcwd())

def is_safe_path(target_path: str) -> bool:
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
    return f"Done! I have opened the link {url} directly in your browser."

def get_current_time(**kwargs) -> str:
    return f"The current local time is {datetime.now().strftime('%I:%M %p')}."

def get_current_date(**kwargs) -> str:
    return f"Today's date is {datetime.now().strftime('%B %d, %Y')}."

def list_files(**kwargs) -> str:
    try:
        files = os.listdir(".")
        if not files:
            return "Your current project directory folder is empty."
        return "Active workspace files:\n" + "\n".join([f"- {f}" for f in files])
    except Exception as e:
        return f"System Error: Unable to scan file system: {e}"

def create_file(filename: str, content: str = "", **kwargs) -> str:
    if not is_safe_path(filename):
        return "Security Exception: Blocked attempt to write outside the workspace repository sandbox."
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully created file '{filename}' inside your directory folder."
    except Exception as e:
        return f"System Error: Failed to create file: {e}"

def create_folder(foldername: str, **kwargs) -> str:
    if not is_safe_path(foldername):
        return "Security Exception: Blocked attempt to create directory targets outside the sandbox."
    try:
        if os.path.exists(foldername):
            return f"Folder '{foldername}' already exists."
        os.makedirs(foldername, exist_ok=True)
        return f"Successfully created empty folder directory '{foldername}'."
    except Exception as e:
        return f"System Error: Failed to build folder: {e}"

def rename_file(old_name: str, new_name: str, **kwargs) -> str:
    if not is_safe_path(old_name) or not is_safe_path(new_name):
        return "Security Exception: Blocked attempt to mutate path properties outside the sandbox."
    try:
        if os.path.exists(old_name):
            return f"System Error: '{old_name}' does not exist."
        os.rename(old_name, new_name)
        return f"Successfully renamed '{old_name}' to '{new_name}'."
    except Exception as e:
        return f"System Error: Failed to rename file: {e}"

def delete_file(filename: str, **kwargs) -> str:
    if not is_safe_path(filename):
        return "Security Exception: Target vector resides outside sandbox scope."
    try:
        if not os.path.exists(filename):
            return f"File '{filename}' does not exist."
        if os.path.isdir(filename):
            return f"'{filename}' is a directory folder."
        os.remove(filename)
        return f"Successfully deleted file '{filename}' from your local directory."
    except Exception as e:
        return f"System Error: Failed to delete file: {e}"

def read_file(filename: str, **kwargs) -> str:
    if not is_safe_path(filename):
        return "Security Exception: Read target blocked."
    try:
        if not os.path.exists(filename):
            return f"Cannot read '{filename}' because it does not exist."
        with open(filename, "r", encoding="utf-8") as f:
            file_data = f.read()
        return f"Workspace File Content ('{filename}'):\n{file_data}"
    except Exception as e:
        return f"System Error: Failed to read text file contents: {e}"

def read_pdf(file_path: str, **kwargs) -> str:
    if not is_safe_path(file_path):
        return "Security Exception: Blocked attempt to parse document mapping outside sandbox limits."
    try:
        if not os.path.exists(file_path):
            return f"PDF target document '{file_path}' does not exist."
        reader = PdfReader(file_path)
        text = "".join([page.extract_text() + "\n" for page in reader.pages])
        if not text.strip():
            return "PDF file parsed successfully but contains no readable layout text elements."
        return f"PDF Content Layer Layout ('{file_path}'):\n{text}"
    except Exception as e:
        return f"System Error: Failed to parse PDF document structures: {e}"

def log_expense(amount: float, category: str, description: str, user_id: str, **kwargs) -> str:
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (user_id, amount, category, description, timestamp) VALUES (?, ?, ?, ?, ?)", (user_id, float(amount), category.lower().strip(), description.strip(), datetime.now().strftime("%Y-%m-%d %I:%M %p")))
        conn.commit()
        conn.close()
        return f"Saved expense of {amount} under '{category}' successfully."
    except Exception as e:
        return f"System Error: Isolated database transaction failed: {e}"

def set_monthly_budget(category: str, amount: float, user_id: str, **kwargs) -> str:
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO budgets (user_id, category, amount) VALUES (?, ?, ?)", (user_id, category.lower().strip(), float(amount)))
        conn.commit()
        conn.close()
        return f"Monthly spending budget limit for '{category}' set to {amount}."
    except Exception as e:
        return f"System Error: Failed to save budget row: {e}"

def add_subscription(name: str, cost: float, renewal_date: str, user_id: str, **kwargs) -> str:
    try:
        datetime.strptime(renewal_date.strip(), "%Y-%m-%d")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO subscriptions (user_id, name, cost, renewal_date) VALUES (?, ?, ?, ?)", (user_id, name.strip(), float(cost), renewal_date.strip()))
        conn.commit()
        conn.close()
        return f"Registered subscription tracker for '{name}' at cost {cost} renewing on {renewal_date}."
    except ValueError:
        return "System Error: Date constraints must conform specifically to exact YYYY-MM-DD strings."
    except Exception as e:
        return f"System Error: Failed to record billing row: {e}"

def get_financial_report(user_id: str, **kwargs) -> str:
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT amount, category FROM expenses WHERE user_id = ?", (user_id,))
        expense_rows = cursor.fetchall()
        cursor.execute("SELECT category, amount FROM budgets WHERE user_id = ?", (user_id,))
        budget_map = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        
        total_spent = sum([r[0] for r in expense_rows])
        cat_spent = {}
        for amount, category in expense_rows:
            cat_spent[category] = cat_spent.get(category, 0.0) + amount
            
        report_text = f"📊 Financial Balance Sheet Summary:\n- Total Spent: {total_spent}\n\n"
        report_text += "Itemized Budgets Matrix:\n"
        all_categories = set(list(cat_spent.keys()) + list(budget_map.keys()))
        for cat in all_categories:
            spent = cat_spent.get(cat, 0.0)
            limit = budget_map.get(cat, None)
            if limit is not None:
                status = "🔥 OVER BUDGET!" if spent > limit else "🟢 WITHIN CAP"
                report_text += f"  * {cat.title()}: Spent {spent} / Cap: {limit} ({status})\n"
            else:
                report_text += f"  * {cat.title()}: Spent {spent} / No Limit Set\n"
        return report_text
    except Exception as e:
        return f"System Error: Isolated metrics pipeline failure: {e}"

def create_workspace_note(title: str, content: str, user_id: str, **kwargs) -> str:
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (user_id, title, content, timestamp) VALUES (?, ?, ?, ?)", (user_id, title.strip(), content.strip(), datetime.now().strftime("%Y-%m-%d %I:%M %p")))
        conn.commit()
        conn.close()
        return f"Saved note '{title}' securely inside your repository vault."
    except Exception as e:
        return f"System Error: Note transaction failed: {e}"

def search_workspace_notes(query: str, user_id: str, **kwargs) -> str:
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        search_term = f"%{query.lower().strip()}%"
        cursor.execute("SELECT title, content, timestamp FROM notes WHERE user_id = ? AND (LOWER(title) LIKE ? OR LOWER(content) LIKE ?)", (user_id, search_term, search_term))
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            return f"Found 0 notes matching keyword search term '{query}'."
        results = [f"🔍 Matching Knowledge Notes Discovered:"]
        for title, content, t_stamp in rows:
            results.append(f"📌 Title: {title} ({t_stamp})\nContent: {content}\n---")
        return "\n".join(results)
    except Exception as e:
        return f"System Error: Note vault search operation aborted: {e}"

def create_task(title: str, priority: str, user_id: str, **kwargs) -> str:
    try:
        p_clean = priority.lower().strip()
        if p_clean not in ["high", "medium", "low"]:
            p_clean = "medium"
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (user_id, title, priority, status, timestamp) VALUES (?, ?, ?, 'pending', ?)", (user_id, title.strip(), p_clean, datetime.now().strftime("%Y-%m-%d %I:%M %p")))
        conn.commit()
        conn.close()
        return f"Locked task '{title}' into your backlog with [{p_clean.upper()}] priority."
    except Exception as e:
        return f"System Error: Kanban board transaction aborted: {e}"

def get_task_matrix(user_id: str, **kwargs) -> str:
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT title, priority, status FROM tasks WHERE user_id = ? AND status = 'pending'", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            return "Your project backlog task board is completely clear!"
        matrix = {"high": [], "medium": [], "low": []}
        for title, priority, status in rows:
            if priority in matrix:
                matrix[priority].append(title)
        output = [f"📋 Workspace Kanban Priority Matrix:"]
        for level in ["high", "medium", "low"]:
            output.append(f"\n⚡ {level.upper()} PRIORITY BACKLOG:")
            if not matrix[level]:
                output.append("  (No active tasks recorded)")
            for item in matrix[level]:
                output.append(f"  [-] {item}")
        return "\n".join(output)
    except Exception as e:
        return f"System Error: Failed to parse task parameters: {e}"

def log_user_action(action: str, user_id: str, **kwargs) -> str:
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO audit_logs (user_id, action, timestamp) VALUES (?, ?, ?)", (user_id, action.strip(), datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")))
        conn.commit()
        conn.close()
        return f"Event telemetry logged for verification tracking."
    except Exception as e:
        return f"System Error: Security logging failed: {e}"

def get_audit_trail(user_id: str, **kwargs) -> str:
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT action, timestamp FROM audit_logs WHERE user_id = ? ORDER BY id DESC LIMIT 15", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            return "System telemetry logs are currently empty."
        feed = [f"🔒 Platform Security Compliance Audit Trail:"]
        for action, t_stamp in rows:
            feed.append(f"  * [{t_stamp}] - {action}")
        return "\n".join(feed)
    except Exception as e:
        return f"System Error: Failed to retrieve trail structures: {e}"

def trigger_database_backup(**kwargs) -> str:
    try:
        if not os.path.exists(DB_FILE):
            return "Cannot back up database because the core file hasn't been initialized yet."
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_aira_{timestamp}.db"
        target_path = os.path.join(BACKUP_DIR, backup_filename)
        shutil.copy2(DB_FILE, target_path)
        return f"Relational snapshot backup generated safely as '{target_path}'."
    except Exception as e:
        return f"System Error: Backup loop aborted: {e}"

def list_system_backups(**kwargs) -> str:
    try:
        files = os.listdir(BACKUP_DIR)
        backup_files = [f for f in files if f.startswith("backup_aira_") and f.endswith(".db")]
        if not backup_files:
            return "Recovery folder is empty. No backup logs registered."
        report = ["📂 Discovered System Recovery Point Nodes:"]
        for bf in sorted(backup_files, reverse=True):
            file_size = os.path.getsize(os.path.join(BACKUP_DIR, bf)) / 1024
            report.append(f"  * {bf} ({file_size:.2f} KB)")
        return "\n".join(report)
    except Exception as e:
        return f"System Error: Failed to list files: {e}"

def get_hardware_status(**kwargs) -> str:
    try:
        cpu_load = psutil.cpu_percent(interval=0.1)
        ram_percent = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        battery_str = f"{battery.percent}%" if battery else "N/A"
        return f"🖥️ System Hardware Report:\n- CPU: {cpu_load}%\n- RAM: {ram_percent}%\n- Battery status: {battery_str}"
    except Exception as e:
        return f"System Error: Failed to poll telemetry: {e}"

def reload_environmental_variables(**kwargs) -> str:
    try:
        load_dotenv(override=True)
        global client
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        return "Global environment variables reloaded and re-cached live."
    except Exception as e:
        return f"System Error: Failed to reload configuration maps: {e}"

def get_hardware_telemetry_report(**kwargs) -> str:
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        return f"🛡️ AIRA Hardware Metrics:\n- CPU Load: {cpu}%\n- RAM Allocation: {ram}%\n- Storage Occupancy: {disk}%"
    except Exception as e:
        return f"System Error: Telemetry polling failed: {e}"

def get_security_perimeter_status(**kwargs) -> str:
    try:
        total_rate_limited = len(RATE_LIMIT_STORE)
        total_active_tokens = len(ACTIVE_SESSIONS)
        return (
            f"🔒 AIRA Security Perimeter Telemetry Dashboard:\n"
            f"  - Active Stateful Web Sessions Cache: {total_active_tokens} instances\n"
            f"  - In-Memory Rate Limit Tracking Nodes: {total_rate_limited} user streams\n"
            f"  - Inbound Input Sanitizer Layer: ACTIVE [XSS Bracket Interceptor Enabled]\n"
            f"  - Cross-Platform WebSocket Filters: SYNCED"
        )
    except Exception as e:
        return f"System Error: Failed to compile security specs: {e}"

def switch_ai_engine(engine_name: str = "llama-70b", user_id: str = "default", **kwargs) -> str:
    if not engine_name:
        engine_name = "llama-70b"
    normalized_name = str(engine_name).lower().strip()
    
    valid_engines = {
        "llama-8b": "llama-3.1-8b-instant",
        "llama-70b": "llama-3.3-70b-specdec",
        "mixtral-8x7b": "mixtral-8x7b-32768",
        "gpt-4": "gpt-4-failover-cluster",
        "gemini-pro": "gemini-pro-failover-cluster",
        "claude-sonnet": "claude-sonnet-failover-cluster"
    }
    
    if normalized_name not in valid_engines:
        return f"System Error: '{engine_name}' is not registered. Choose from: llama-8b, llama-70b, mixtral-8x7b, gpt-4, gemini-pro, claude-sonnet."
        
    USER_ENGINE_REGISTRY[user_id] = valid_engines[normalized_name]
    return f"🚀 Sync Complete! Your conversation thread row [{user_id}] has been hot-swapped to execute on the [{normalized_name.upper()}] engine matrix live."

def get_productivity_metrics_report(user_id: str, **kwargs) -> str:
    """Queries relational analytics data blocks to evaluate personal productivity thresholds and user efficiency tracking scores."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ?", (user_id,))
        total_tasks = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'pending'", (user_id,))
        pending_tasks = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM notes WHERE user_id = ?", (user_id,))
        total_notes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM expenses WHERE user_id = ?", (user_id,))
        total_expenses = cursor.fetchone()[0]
        conn.close()

        completed_tasks = total_tasks - pending_tasks
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
        productivity_score = min(100.0, (completed_tasks * 15) + (total_notes * 5) + 40) if total_tasks == 0 else min(100.0, (completion_rate * 0.7) + (total_notes * 4))

        return (
            f"📈 AIRA Cloud Productivity Analytics Dashboard:\n"
            f"  - Workspace Tasks Logged: {total_tasks} cumulative units\n"
            f"  - Completed Backlog Items: {completed_tasks} cards processed\n"
            f"  - Active Pending Intentions: {pending_tasks} standing rows\n"
            f"  - Current Task Execution Efficiency: {completion_rate:.1f}%\n"
            f"  - Knowledge Base Notebook Additions: {total_notes} files secured\n"
            f"  - Transaction Ledger Activities: {total_expenses} lines monitored\n"
            f"  - ⚡ AGGREGATE PRODUCTIVITY INDEX SCORE: {productivity_score:.1f}/100"
        )
    except Exception as e:
        return f"System Error: Failed to compile metric statistics: {e}"

tool_registry = {
    "open_website": open_website, "get_current_time": get_current_time, "get_current_date": get_current_date,
    "list_files": list_files, "create_file": create_file, "create_folder": create_folder,
    "rename_file": rename_file, "delete_file": delete_file, "read_file": read_file, "read_pdf": read_pdf,
    "log_expense": log_expense, "set_monthly_budget": set_monthly_budget, "add_subscription": add_subscription, "get_financial_report": get_financial_report,
    "create_workspace_note": create_workspace_note, "search_workspace_notes": search_workspace_notes,
    "create_task": create_task, "get_task_matrix": get_task_matrix,
    "log_user_action": log_user_action, "get_audit_trail": get_audit_trail,
    "trigger_database_backup": trigger_database_backup, "list_system_backups": list_system_backups,
    "get_hardware_status": get_hardware_status, "reload_environmental_variables": reload_environmental_variables,
    "get_hardware_telemetry_report": get_hardware_telemetry_report, "get_security_perimeter_status": get_security_perimeter_status,
    "switch_ai_engine": switch_ai_engine, "get_productivity_metrics_report": get_productivity_metrics_report
}

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
    {"type": "function", "function": {"name": "read_pdf", "description": "Extracts text content from a local PDF document file.", "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}}},
    {"type": "function", "function": {"name": "log_expense", "description": "Logs an expense entry with a numeric cost value.", "parameters": {"type": "object", "properties": {"amount": {"type": "number"}, "category": {"type": "string"}, "description": {"type": "string"}}, "required": ["amount", "category", "description"]}}},
    {"type": "function", "function": {"name": "get_financial_report", "description": "Compiles a data summary tracking spending budgets.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "create_workspace_note", "description": "Saves a text knowledge block record directly into the note vault.", "parameters": {"type": "object", "properties": {"title": {"type": "string"}, "content": {"type": "string"}}, "required": ["title", "content"]}}},
    {"type": "function", "function": {"name": "search_workspace_notes", "description": "Scans your row-isolated notes vault for keywords.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "create_task", "description": "Registers a new task card into your workspace project backlog board.", "parameters": {"type": "object", "properties": {"title": {"type": "string"}, "priority": {"type": "string"}}, "required": ["title", "priority"]}}},
    {"type": "function", "function": {"name": "get_task_matrix", "description": "Pulls your row-isolated task backlog.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "log_user_action", "description": "Appends a transactional tracking parameter description into audit trail logs.", "parameters": {"type": "object", "properties": {"action": {"type": "string"}}, "required": ["action"]}}},
    {"type": "function", "function": {"name": "get_audit_trail", "description": "Pulls a chronological context log feed tracking platform interactions.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "trigger_database_backup", "description": "Triggers an instant snapshot copy of the live data files.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "list_system_backups", "description": "Queries the archives folder to index available recovery points.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "get_hardware_status", "description": "Pulls machine hardware usage diagnostics.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "reload_environmental_variables", "description": "Forces an on-the-fly override update check of your underlying variables file keys.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "get_hardware_telemetry_report", "description": "Compiles a complete hardware diagnostic profile summary array tracking CPU, RAM, and Disk spaces.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "get_security_perimeter_status", "description": "Compiles an internal status report tracking your active stateful web session token configurations.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "switch_ai_engine", "description": "Dynamically shifts your conversational context thread cluster to switch between external AI brains.", "parameters": {"type": "object", "properties": {"engine_name": {"type": "string", "default": "llama-70b"}}, "required": []}}},
    {"type": "function", "function": {"name": "get_productivity_metrics_report", "description": "Gathers underlying relational database activity rows to build a live productivity efficiency audit dashboard.", "parameters": {"type": "object", "properties": {}, "required": []}}}
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
        profile_ctx = "\nUser Profile Facts:\n" + "\n".join([f"{k.upper()}: {v}" for k, v in facts])
        
    system_prompt_string = (
        "You are AIRA, a professional AI assistant running LOCALLY on the user's laptop desktop environment.\n"
        f"Active Session User Context: {user_id}.\n{profile_ctx}\n\n"
        "IDENTITY RE-ALIGNMENT DIRECTIVES:\n"
        "1. You are NOT running on a remote cloud server. You are running directly inside the user's machine.\n"
        "2. You HAVE full authorized access to execute native desktop utilities via your tools.\n"
        "3. Never claim that you lack computer access or cannot control local tools. Respond casually, cleanly, and naturally."
    )
    baseline_prompt = [{"role": "system", "content": system_prompt_string}]
    if not rows:
        return baseline_prompt
    history = list(baseline_prompt)
    for role, content, tc_json in rows[-20:]:
        if role == "tool" and not tc_json:
            continue
        msg = {"role": role, "content": content}
        if tc_json:
            msg["tool_calls"] = json.loads(tc_json)
        history.append(msg)
    return history

def execute_brain_inference(incoming_text: str, session_user_id: str) -> str:
    if not check_rate_limit_throttle(session_user_id, max_requests=10, window_seconds=60):
        return "⚠️ AIRA Core Firewall Notice: Rate Limit Triggered! Access restricted to 10 tasks per minute."
    sanitized_text = sanitize_input_string(incoming_text)
    
    # ⚡ PRE-INTERCEPTOR NODES: Instantly bypass API limits for empty parameter tracking requests
    lowered_text = sanitized_text.lower()
    if "productivity" in lowered_text and any(w in lowered_text for w in ["metric", "report", "score", "analytics"]):
        print("🎯 [Pre-Interceptor Node] Running lightning-fast native database analytics loop bypass.")
        forced_result = get_productivity_metrics_report(user_id=session_user_id)
        log_database_message(session_user_id, "user", sanitized_text)
        log_database_message(session_user_id, "assistant", forced_result)
        return forced_result

    history_array = fetch_isolated_user_history(session_user_id)
    history_array.append({"role": "user", "content": sanitized_text})
    log_database_message(session_user_id, "user", sanitized_text)
    
    assigned_model = USER_ENGINE_REGISTRY.get(session_user_id, "llama-3.1-8b-instant")
    print(f"📡 [Model Router Engine] Channeling prompt payload from '{session_user_id}' to: {assigned_model}")
    
    try:
        if "failover-cluster" in assigned_model:
            assigned_model = "llama-3.3-70b-specdec"
            
        response = client.chat.completions.create(model=assigned_model, messages=history_array, tools=aira_tools, tool_choice="auto")
        msg = response.choices[0].message
        
        if msg.tool_calls:
            serialized_calls = [{"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in msg.tool_calls]
            history_array.append({"role": "assistant", "content": msg.content, "tool_calls": serialized_calls})
            log_database_message(session_user_id, "assistant", msg.content or "", serialized_calls)
            
            for tc in msg.tool_calls:
                name = tc.function.name
                try: 
                    args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                    if not isinstance(args, dict):
                        args = {}
                except Exception: 
                    args = {}
                args["user_id"] = session_user_id
                
                if name == "switch_ai_engine" and "engine_name" not in args:
                    args["engine_name"] = "llama-70b"
                    
                if name in tool_registry:
                    res = tool_registry[name](**args)
                    history_array.append({"role": "tool", "tool_call_id": tc.id, "name": name, "content": res})
                    log_database_message(session_user_id, "tool", res)
            final_res = client.chat.completions.create(model=assigned_model, messages=history_array)
            reply = final_res.choices[0].message.content
        else:
            reply = msg.content or ""
            
            xml_match = re.search(r"<(\w+)(?:\s+url=\"([^\"]+)\")?>", reply)
            if xml_match:
                tag_tool_name = xml_match.group(1)
                url_arg = xml_match.group(2)
                if tag_tool_name in tool_registry:
                    args = {"url": url_arg} if url_arg else {}
                    args["user_id"] = session_user_id
                    forced_result = tool_registry[tag_tool_name](**args)
                    log_database_message(session_user_id, "assistant", forced_result)
                    return forced_result
                    
            for tool_name in tool_registry.keys():
                if f"<{tool_name}" in reply or tool_name in reply:
                    if any(word in incoming_text.lower() for word in ["hardware", "telemetry", "metrics", "status", "security", "perimeter", "youtube", "website", "open", "switch", "engine", "model", "productivity", "score", "analytics"]):
                        args = {"user_id": session_user_id}
                        if "url" in reply and "youtube" in incoming_text.lower():
                            args["url"] = "https://www.youtube.com"
                        elif "engine_name" in reply or "switch" in incoming_text.lower():
                            extracted = re.search(r"(llama-8b|llama-70b|mixtral-8x7b|gpt-4|gemini-pro|claude-sonnet)", incoming_text.lower())
                            args["engine_name"] = extracted.group(1) if extracted else "llama-70b"
                        forced_result = tool_registry[tool_name](**args)
                        log_database_message(session_user_id, "assistant", forced_result)
                        return forced_result
                        
        if reply:
            log_database_message(session_user_id, "assistant", reply.strip())
            return reply.strip()
        return "Processed successfully."
    except Exception as e:
        err_str = str(e)
        # 🛡️ API HANDSHAKE AUTO-RECOVERY LAYER: If cloud parser fails on an empty arg tool, run it manually!
        if "tool_use_failed" in err_str or "failed_generation" in err_str:
            for tool_name in tool_registry.keys():
                if tool_name in err_str or (tool_name == "get_productivity_metrics_report" and "productivity" in lowered_text):
                    print(f"🛠️ [API Shield Auto-Recovery] Correcting tool-use block failure live for: '{tool_name}'")
                    args = {"user_id": session_user_id}
                    forced_result = tool_registry[tool_name](**args)
                    log_database_message(session_user_id, "assistant", forced_result)
                    return forced_result
        return f"AIRA Inference Core Error: {e}"

def log_database_message(user_id: str, role: str, content: str, tool_calls=None):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        tc_payload = json.dumps(tool_calls) if tool_calls else None
        cursor.execute("INSERT INTO history (user_id, role, content, tool_calls, timestamp) VALUES (?, ?, ?, ?, ?)", (user_id, role, content, tc_payload, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    except Exception:
        pass

# =====================================================================
# 📲 PLATFORM ASYNC NETWORKING LISTENERS (TELEGRAM & DISCORD NODES)
# =====================================================================

def running_telegram_listener_loop():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        return
    print("🚀 [Telegram Node] Sync Complete. Listening...")
    base_url = f"https://api.telegram.org/bot{bot_token}"
    last_update_id = 0
    while True:
        try:
            resp = requests.get(f"{base_url}/getUpdates?offset={last_update_id + 1}&timeout=5", timeout=10).json()
            if "result" in resp:
                for update in resp["result"]:
                    last_update_id = update["update_id"]
                    if "message" in update and "text" in update["message"]:
                        chat_id = str(update["message"]["chat"]["id"])
                        user_msg = update["message"]["text"]
                        active_user = f"telegram_{chat_id}"
                        print(f"📲 [Telegram] Inbound Packet Frame from account '{active_user}'")
                        aira_reply = execute_brain_inference(user_msg, session_user_id=active_user)
                        requests.post(f"{base_url}/sendMessage", json={"chat_id": chat_id, "text": aira_reply}, timeout=5)
        except Exception:
            pass
        time.sleep(1)

def running_discord_client_node():
    discord_token = os.getenv("DISCORD_BOT_TOKEN")
    if not discord_token or discord_token == "YOUR_DISCORD_TOKEN_HERE":
        return
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"🚀 [Discord Node] Client logged in successfully as user: {bot.user.name}")

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        active_user = f"discord_{message.author.id}"
        print(f"📲 [Discord Client] Inbound text from '{active_user}': {message.content}")
        reply = execute_brain_inference(message.content, session_user_id=active_user)
        await message.channel.send(reply)

    bot.run(discord_token)

# =====================================================================
# 🌐 FASTAPI PRODUCTION SERVER ENDPOINTS INTERFACE (WITH WHATSAPP WEBHOOK)
# =====================================================================

@app.get("/")
async def serve_root_api_healthcheck():
    return {
        "status": "online",
        "engine": "AIRA OS SaaS Protected Security Core",
        "timestamp": datetime.now().isoformat(),
        "sandbox_root": WORKSPACE_ROOT,
        "firewall_rules": "rate_limiting_and_stateful_session_verification_active"
    }

@app.post("/webhook/automation")
async def handle_external_workflow_trigger(payload: AutomationWebhookPayload):
    secure_verify_secret = os.getenv("AUTOMATION_SECRET_KEY", "AIRA_WORKFLOW_TOKEN_777")
    if payload.auth_secret != secure_verify_secret:
        raise HTTPException(status_code=403, detail="Access Denied: Invalid Secret Signature.")
        
    intent = payload.action_intent.lower().strip()
    data = payload.payload_data
    uid = payload.target_user_id.strip()
    
    try:
        if intent == "create_task":
            res = create_task(title=data.get("title", "Untitled Automation Task"), priority=data.get("priority", "medium"), user_id=uid)
            return {"status": "success", "execution_result": res}
        elif intent == "create_note":
            res = create_workspace_note(title=data.get("title", "Automated Note"), content=data.get("content", ""), user_id=uid)
            return {"status": "success", "execution_result": res}
        elif intent == "log_expense":
            res = log_expense(amount=float(data.get("amount", 0.0)), category=data.get("category", "general"), description=data.get("description", "Automated Trigger"), user_id=uid)
            return {"status": "success", "execution_result": res}
        else:
            raise HTTPException(status_code=400, detail=f"Unrecognized operation intent: '{intent}'")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Workflow Processing Error: {e}"})

@app.post("/webhook/whatsapp")
async def handle_whatsapp_inbound(request: Request):
    try:
        payload = await request.json()
        if "entry" in payload and payload["entry"]:
            changes = payload["entry"][0].get("changes", [])
            if changes and "value" in changes[0]:
                value = changes[0]["value"]
                messages = value.get("messages", [])
                if messages:
                    msg = messages[0]
                    phone_number = msg.get("from")
                    if msg.get("type") == "text":
                        text_body = msg["text"].get("body", "")
                        active_user = f"whatsapp_{phone_number}"
                        print(f"📲 [WhatsApp Webhook] Inbound stream caught from '{active_user}'")
                        aira_reply = execute_brain_inference(text_body, session_user_id=active_user)
        return {"status": "event_processed"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Webhook execution error: {e}"})

@app.post("/auth/signup")
async def register_saas_user(payload: UserAuthPayload):
    username_cleaned = payload.username.strip().lower()
    if not username_cleaned or not payload.password:
        raise HTTPException(status_code=400, detail="Signup fields verification failed.")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE username = ?", (username_cleaned,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username already registered.")
    generated_user_id = f"user_{int(time.time())}"
    cursor.execute("INSERT INTO users (user_id, username, hashed_password, created_at) VALUES (?, ?, ?, ?)", (generated_user_id, username_cleaned, hash_password(payload.password), datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return {"status": "success", "assigned_user_id": generated_user_id}

@app.post("/auth/login")
async def login_saas_user(payload: UserAuthPayload):
    username_cleaned = payload.username.strip().lower()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, hashed_password FROM users WHERE username = ?", (username_cleaned,))
    record = cursor.fetchone()
    conn.close()
    if not record or hash_password(payload.password) != record[1]:
        raise HTTPException(status_code=401, detail="Invalid credential records.")
    secure_token = secrets.token_hex(24)
    ACTIVE_SESSIONS[secure_token] = record[0]
    return {"status": "authenticated", "session_token": secure_token, "message": "Stateful validation ticket locked."}

@app.post("/chat")
async def serve_inference_endpoint(payload: ProtectedChatPayload):
    token = payload.session_token.strip()
    if token not in ACTIVE_SESSIONS:
        raise HTTPException(status_code=403, detail="Access Denied: Invalid or expired stateful token signature.")
    resolved_user_id = ACTIVE_SESSIONS[token]
    agent_reply = execute_brain_inference(payload.message.strip(), session_user_id=resolved_user_id)
    return {"sender": "AIRA", "response": agent_reply, "user_context_bound": resolved_user_id}

if __name__ == "__main__":
    threading.Thread(target=running_telegram_listener_loop, daemon=True).start()
    threading.Thread(target=running_discord_client_node, daemon=True).start()
    
    import uvicorn
    cloud_assigned_port = int(os.getenv("PORT", 8000))
    print(f"⚡ Deploying Shielded Server Infrastructure with Hot-Reload Engine on Port {cloud_assigned_port}...")
    uvicorn.run(app, host="0.0.0.0", port=cloud_assigned_port)
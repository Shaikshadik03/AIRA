import os
import json
import webbrowser  # Preserved V4: Native tool use to open browser windows
from datetime import datetime  # Preserved V4: Native tool use to access system clock
from dotenv import load_dotenv
from groq import Groq
from ddgs import DDGS      # Preserved V3: DuckDuckGo Search Engine
from pypdf import PdfReader  # Preserved V3: PDF Reader Document Extractor
import psutil              # Preserved V4: Hardware telemetry engine

# Load environment variables from your .env file
load_dotenv()

# Initialize the Groq cloud communication client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Persistent Memory Storage Pointers
MEMORY_FILE = "memory.json"
PROFILE_FILE = "profile.json"
DEADLINES_FILE = "deadlines.json"

# =====================================================================
# 🚀 AIRA V6 SYSTEM — AGENT ACTION TOOL CORES
# =====================================================================

# 1. Core Python System-Level Action Functions
def open_website(url: str) -> str:
    """Opens any specified website URL in the user's default browser safely."""
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    webbrowser.open(url)
    return f"System message: Successfully opened {url} in Shadik's desktop browser."

def get_current_time() -> str:
    """Retrieves the current local clock time from the laptop system clock."""
    now = datetime.now()
    formatted_time = now.strftime("%I:%M %p")
    return f"System message: The current local time is {formatted_time}."

def get_current_date() -> str:
    """Retrieves the current local calendar date from the laptop system clock."""
    now = datetime.now()
    formatted_date = now.strftime("%B %d, %Y")
    return f"System message: Today's date is {formatted_date}."

def list_files() -> str:
    """Scans the current project directory and returns a list of all files inside."""
    try:
        files = os.listdir(".")
        if not files:
            return "System message: The current directory workspace folder is entirely empty."
        bulleted_files = "\n".join([f"- {item}" for item in files])
        return f"System message: Here are the active workspace files found:\n{bulleted_files}"
    except Exception as e:
        return f"System Error: Unable to scan file system profile. Reason: {e}"

def create_file(filename: str, content: str = "") -> str:
    """Creates a new text file inside the local project workspace folder."""
    try:
        if "/" in filename or "\\" in filename:
            return "System Error: Security violation. Files must be created directly in the workspace root."
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"System message: Successfully created file '{filename}' inside the workspace directory."
    except Exception as e:
        return f"System Error: Failed to execute file creation payload. Reason: {e}"

def create_folder(foldername: str) -> str:
    """Creates a brand-new directory folder inside the local project workspace folder."""
    try:
        if "/" in foldername or "\\" in foldername:
            return "System Error: Security violation. Folders must be created directly inside the workspace root."
        if os.path.exists(foldername):
            return f"System message: A folder named '{foldername}' already exists in this directory."
            
        os.makedirs(foldername, exist_ok=True)
        return f"System message: Successfully created a new empty folder directory named '{foldername}'."
    except Exception as e:
        return f"System Error: Failed to build folder directory. Reason: {e}"

def rename_file(old_name: str, new_name: str) -> str:
    """Renames an existing file or folder inside the local project workspace folder."""
    try:
        if "/" in old_name or "\\" in old_name or "/" in new_name or "\\" in new_name:
            return "System Error: Security violation. Renaming must be done strictly within the workspace root."
        if not os.path.exists(old_name):
            return f"System Error: Cannot rename '{old_name}' because it does not exist in this folder."
            
        os.rename(old_name, new_name)
        return f"System message: Successfully renamed '{old_name}' to '{new_name}' safely."
    except Exception as e:
        return f"System Error: Failed to change target file name profile. Reason: {e}"

def delete_file(filename: str) -> str:
    """Deletes an existing file document from the workspace root safely."""
    try:
        if "/" in filename or "\\" in filename:
            return "System Error: Security violation. Deletion targets must live inside the workspace root."
        if not os.path.exists(filename):
            return f"System Error: File '{filename}' cannot be deleted because it does not exist."
        if os.path.isdir(filename):
            return f"System Error: '{filename}' is a directory folder. Standard file deletion commands cannot delete folders."
            
        os.remove(filename)
        return f"System message: Successfully dropped and deleted file '{filename}' from the local directory layout."
    except Exception as e:
        return f"System Error: Failed to execute secure file deletion task. Reason: {e}"

def read_file(filename: str) -> str:
    """Reads and returns the complete plain text content of a target workspace file document."""
    try:
        if "/" in filename or "\\" in filename:
            return "System Error: Security violation. Reading targets must live directly within the workspace root."
        if not os.path.exists(filename):
            return f"System Error: Cannot read file '{filename}' because it does not exist."
        if os.path.isdir(filename):
            return f"System Error: '{filename}' is a directory folder structure, not a text file data block."
            
        with open(filename, "r", encoding="utf-8") as f:
            file_data = f.read()
        return f"Workspace File Execution Payload ('{filename}'):\n{file_data}"
    except Exception as e:
        return f"System Error: Failed to extract internal text string matrix. Reason: {e}"

def get_hardware_status() -> str:
    """Gathers dynamic hardware utilization statistics like CPU load, RAM use, and Battery life."""
    try:
        cpu_load = psutil.cpu_percent(interval=0.5)
        ram_percent = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        
        if battery is not None:
            plugged_in = "Plugged In Charging" if battery.power_plugged else "Running on Battery Power"
            battery_str = f"{battery.percent}% ({plugged_in})"
        else:
            battery_str = "No physical battery detected (Desktop PC Core Engine)"
            
        return (
            "System Hardware Statistics Report:\n"
            f"- CPU Processing Load: {cpu_load}%\n"
            f"- RAM Memory Utilization: {ram_percent}%\n"
            f"- Power/Battery Profile: {battery_str}"
        )
    except Exception as e:
        return f"System Error: Failed to poll machine telemetry arrays. Reason: {e}"

def launch_app(app_name: str) -> str:
    """Spawns a local native desktop application process on Windows safely using Shell Execution."""
    try:
        app_lookup = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "task_manager": "taskmgr.exe",
            "chrome": "chrome.exe",
            "vs_code": "code",
            "snipping_tool": "snippingtool.exe",
            "settings": "ms-settings:",
            "whatsapp": "whatsapp:",
            "camera": "microsoft.windows.camera:",
            "clock": "ms-clock:"
        }
        
        target_clean_name = app_name.lower().strip()
        
        if "claude" in target_clean_name:
            try:
                os.startfile("claude.exe")
                return "System message: Successfully deployed and executed native Claude desktop app window."
            except Exception:
                webbrowser.open("https://claude.ai")
                return "System message: Local shortcut path wasn't open. Successfully fell back to launching Claude AI via web browser."
        
        if target_clean_name in app_lookup:
            executable = app_lookup[target_clean_name]
            os.startfile(executable)
            return f"System message: Successfully launched local execution process for '{target_clean_name}'."
        else:
            return f"System Error: '{app_name}' is not registered in the safe app registry profile layout."
    except Exception as e:
        return f"System Error: Failed to spawn system app interface. Reason: {e}"

def save_profile_fact(fact_key: str, fact_value: str) -> str:
    """Saves a permanent fact about the user into their long-term profile memory database."""
    try:
        profile = {}
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                try:
                    profile = json.load(f)
                except Exception:
                    profile = {}
                    
        profile[fact_key.lower().strip()] = fact_value.strip()
        
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=4)
        return f"System message: Long-term fact securely saved: '{fact_key}' = '{fact_value}'."
    except Exception as e:
        return f"System Error: Failed to write data to long-term memory file. Reason: {e}"

def read_profile_facts() -> str:
    """Reads all permanently stored profile facts about the user from the long-term database file."""
    try:
        if not os.path.exists(PROFILE_FILE):
            return "System message: Long-term profile memory database file is currently entirely empty."
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            try:
                profile = json.load(f)
            except Exception:
                return "System message: Long-term database is empty or unreadable."
                
        if not profile:
            return "System message: Long-term profile memory database file is currently empty."
            
        formatted_facts = "\n".join([f"- {k.title()}: {v}" for k, v in profile.items()])
        return f"Long-Term Database Scan Output:\n{formatted_facts}"
    except Exception as e:
        return f"System Error: Failed to parse permanent long-term memory registers. Reason: {e}"

def add_deadline(event_name: str, target_date: str) -> str:
    """Saves an upcoming exam, milestone, or hackathon target date (Format: YYYY-MM-DD)."""
    try:
        datetime.strptime(target_date.strip(), "%Y-%m-%d")
        deadlines = {}
        if os.path.exists(DEADLINES_FILE):
            with open(DEADLINES_FILE, "r", encoding="utf-8") as f:
                try:
                    deadlines = json.load(f)
                except Exception:
                    deadlines = {}
                    
        deadlines[event_name.strip()] = target_date.strip()
        with open(DEADLINES_FILE, "w", encoding="utf-8") as f:
            json.dump(deadlines, f, indent=4)
        return f"System message: Deadline registered successfully for '{event_name}' on {target_date}."
    except ValueError:
        return "System Error: Invalid calendar structure layout. Target dates must be written exactly as YYYY-MM-DD."
    except Exception as e:
        return f"System Error: Failed to update scheduler register registry. Reason: {e}"

def get_countdown_alerts() -> str:
    """Calculates real-world time-remaining differences against the machine clock."""
    try:
        if not os.path.exists(DEADLINES_FILE):
            return "System message: No target deadlines are currently registered inside the planner profile."
        with open(DEADLINES_FILE, "r", encoding="utf-8") as f:
            deadlines = json.load(f)
        if not deadlines:
            return "System message: No target deadlines are currently tracking inside the file array."
            
        today = datetime.now().date()
        countdown_report = ["Live Scheduler Tracking Countdown Array:"]
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
        return f"System Error: Failed to process timeline array differences. Reason: {e}"

def search_internet(query: str) -> str:
    """🌟 LEVEL 6: Connects AIRA autonomously to the live web to fetch summaries on news, hackathons, and internships."""
    try:
        print(f"🔍 [Autonomous Tool Execution] Scanning web index pages for: '{query}'...")
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=4)]
            if not results:
                return "System message: The web search query completed but returned 0 active text results."
            search_text = "Live Search Engine Indexes Retrieved:\n"
            for r in results:
                search_text += f"Title: {r['title']}\nSnippet: {r['body']}\n\n"
            return search_text
    except Exception as e:
        return f"System Error: Failed to complete live internet search task. Reason: {e}"


# 2. Scalable Tool Registry Directory Mapping
tool_registry = {
    "open_website": open_website,
    "get_current_time": get_current_time,
    "get_current_date": get_current_date,
    "list_files": list_files,
    "create_file": create_file,
    "create_folder": create_folder,
    "rename_file": rename_file,
    "delete_file": delete_file,
    "read_file": read_file,
    "get_hardware_status": get_hardware_status,
    "launch_app": launch_app,
    "save_profile_fact": save_profile_fact,
    "read_profile_facts": read_profile_facts,
    "add_deadline": add_deadline,
    "get_countdown_alerts": get_countdown_alerts,
    "search_internet": search_internet  # Level 6 Registered!
}

# 3. Dynamic Native AI Agent Tool Blueprints
aira_tools = [
    {
        "type": "function",
        "function": {
            "name": "open_website",
            "description": "Opens any web URL in the browser.",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Returns the current local real-world time.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "Returns the current local real-world date.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Lists all file documents inside the current project workspace directory.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Creates a brand-new file in the local project workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_folder",
            "description": "Creates a brand-new folder directory in the local project workspace directory.",
            "parameters": {
                "type": "object",
                "properties": {"foldername": {"type": "string"}},
                "required": ["foldername"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rename_file",
            "description": "Renames an existing file or folder inside the workspace layout.",
            "parameters": {
                "type": "object",
                "properties": {
                    "old_name": {"type": "string"},
                    "new_name": {"type": "string"}
                },
                "required": ["old_name", "new_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Deletes an existing file document completely from the local folder workspace environment.",
            "parameters": {
                "type": "object",
                "properties": {"filename": {"type": "string"}},
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads the plain text string data stored inside an existing text file doc.",
            "parameters": {
                "type": "object",
                "properties": {"filename": {"type": "string"}},
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_hardware_status",
            "description": "Pulls live diagnostic telemetry parameters regarding the laptop hardware status.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "launch_app",
            "description": "Spawns and launches a local native desktop application program on the user's computer workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "Allowed choices: 'notepad', 'calculator', 'paint', 'task_manager', 'chrome', 'vs_code', 'snipping_tool', 'settings', 'whatsapp', 'camera', 'clock', 'claude'."
                    }
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_profile_fact",
            "description": "Permanently saves a key background fact about the user to a long-term file layout.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fact_key": {"type": "string"},
                    "fact_value": {"type": "string"}
                },
                "required": ["fact_key", "fact_value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_profile_facts",
            "description": "Pulls and reads all long-term saved profile data facts currently held in the database register.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_deadline",
            "description": "Saves an upcoming exam, countdown tracker, assignment milestone, or hackathon target date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_name": {"type": "string"},
                    "target_date": {"type": "string"}
                },
                "required": ["event_name", "target_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_countdown_alerts",
            "description": "Runs a real-time calendar date tracking analysis difference function against stowed planner arrays.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_internet",
            "description": "🌟 LEVEL 6: Browses live web engines dynamically. Use this whenever the user asks for the latest news, tech updates, open internship roles, or coding contests/hackathons happening right now.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The target keyword string text to find online. Example: 'latest AI news 2026' or 'student coding hackathons 2026'."}
                },
                "required": ["query"]
            }
        }
    }
]

# =====================================================================
# 🌐 AIRA SYSTEM — CONTEXT EXTRACTION HELPER FUNCTIONS
# =====================================================================

def read_pdf(file_path: str) -> str:
    """Extracts raw text content out of any local target PDF file."""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"System Error: Failed to parse PDF document. Reason: {e}"

# =====================================================================
# 💾 AIRA SYSTEM — COMPACTION OPTIMIZATION LOGIC
# =====================================================================
def auto_compact_history(history, groq_client):
    """LEVEL 4 ENGINE: Compresses middle logs to guarantee elite execution speeds."""
    if len(history) <= 20:
        return history
    print("\n⚡ [Memory Optimizer Triggered] Short-term history is getting too long!")
    try:
        system_prompt = history[0]
        slice_to_compress = history[1:-4]  
        recent_messages = history[-4:]
        
        raw_text_to_condense = ""
        for msg in slice_to_compress:
            role = msg.get("role", "user").upper()
            content = msg.get("content") or ""
            if msg.get("tool_calls"):
                content += " [System Tool Invocations Executed]"
            raw_text_to_condense += f"{role}: {content}\n"
            
        compaction_prompt = (
            "You are an elite system background memory manager.\n"
            "Analyze the conversational timeline history below, and condense it entirely into a "
            "single, tight narrative paragraph focusing exclusively on key topics decided or files changed.\n\n"
            f"Timeline logs to compress:\n{raw_text_to_condense}"
        )
        compaction_response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Level 4 Pro-Move: Light model for compaction speed
            messages=[{"role": "system", "content": compaction_prompt}]
        )
        compressed_summary = compaction_response.choices[0].message.content
        print("✅ Distillation complete! Saved workspace chat capacity.\n")
        optimized_history = [
            system_prompt,
            {"role": "system", "content": f"Summary profile of previous interactions: {compressed_summary}"}
        ]
        optimized_history.extend(recent_messages)
        return optimized_history
    except Exception as e:
        print(f"⚠️ Memory compaction routine skipped. Reason: {e}")
        return history

# =====================================================================
# 💾 AIRA SYSTEM — PERSISTENT STORAGE MEMORY LOADER & FACT INJECTION
# =====================================================================
loaded_profile_context = ""
if os.path.exists(PROFILE_FILE):
    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        try:
            profile_data = json.load(f)
            if profile_data:
                facts_list = [f"{k.upper()}: {v}" for k, v in profile_data.items()]
                loaded_profile_context = "\nKnown user profile background data:\n" + "\n".join(facts_list)
        except Exception:
            pass

DEFAULT_SYSTEM_PROMPT = [
    {
        "role": "system", 
        "content": (
            "You are AIRA, a professional and highly capable AI agent built by Shadik. "
            "Respond directly and concisely. Balance helpful technical insight with adaptive candor and a touch of wit. "
            f"You are talking directly to Shadik on his personal computer. {loaded_profile_context}\n\n"
            "Natively incorporate this context into your tone. Keep response processing efficient, and use tools automatically when required."
        )
    }
]

if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        try:
            conversation_history = json.load(f)
            print("🤖 Loaded previous memory layout successfully!")
            if conversation_history and conversation_history[0]["role"] == "system":
                conversation_history[0] = DEFAULT_SYSTEM_PROMPT[0]
        except Exception:
            conversation_history = list(DEFAULT_SYSTEM_PROMPT)
            print("⚠️ Memory file was unreadable. Started with fresh profile.")
else:
    conversation_history = list(DEFAULT_SYSTEM_PROMPT)

if loaded_profile_context:
    print("🧠 Long-term user profile background facts injected into the system prompt core!")

print("\n⚡ AIRA is online and running! Type 'exit' to cleanly close down.")
print("🌐 Ask questions naturally—AIRA will search the internet autonomously when required.")
print("📄 Format PDF document readings as: 'pdf: filename.pdf'\n")

# =====================================================================
# 💬 AIRA SYSTEM — INTERACTIVE MAIN LOOP
# =====================================================================
while True:
    conversation_history = auto_compact_history(conversation_history, client)
    user_input = input("You: ").strip()
    
    if user_input.lower() == "exit":
        print("💾 Saving conversation logs securely to disk... Goodbye Shadik!")
        with open(MEMORY_FILE, "w") as f:
            json.dump(conversation_history, f)
        break

    if not user_input:
        continue

    if user_input.startswith("pdf:"):
        file_name = user_input[4:].strip()
        print(f"📄 Scraping text content out of target document: '{file_name}'...")
        pdf_extracted_text = read_pdf(file_name)
        prompt_with_context = f"Here is the PDF content from file '{file_name}':\n\n{pdf_extracted_text}\n\nAnalyze and break down this data concisely for the user."
        conversation_history.append({"role": "user", "content": prompt_with_context})
    else:
        conversation_history.append({"role": "user", "content": user_input})

    try:
        # Level 4 Pro-Move Swap: Utilizing high-speed engine layer to optimize token longevity
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=conversation_history,
            tools=aira_tools,        
            tool_choice="auto"       
        )
        
        message = response.choices[0].message
        
        if message.tool_calls:
            print("\n🤖 [AIRA Agent Mode Triggered!]")
            serialized_tool_calls = []
            for tool_call in message.tool_calls:
                serialized_tool_calls.append({
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                })
            
            conversation_history.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": serialized_tool_calls
            })
            
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                try:
                    func_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                except Exception:
                    func_args = {}
                
                if not func_args or not isinstance(func_args, dict):
                    func_args = {}
                
                print(f"👉 Dynamic Registry Lookup: Executing tool '{func_name}'")
                print(f"👉 Arguments extracted from Groq context: {func_args}")
                
                if func_name in tool_registry:
                    action_function = tool_registry[func_name]
                    execution_result = action_function(**func_args)  
                    
                    conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": execution_result
                    })
            
            print("⏳ Feeding action results back to AIRA for confirmation text assembly...")
            final_response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=conversation_history
            )
            final_reply = final_response.choices[0].message.content
            print(f"\nAIRA: {final_reply}\n")
            conversation_history.append({"role": "assistant", "content": final_reply})
            continue  
            
        ai_reply = message.content
        if ai_reply:
            print(f"\nAIRA: {ai_reply}\n")
            conversation_history.append({"role": "assistant", "content": ai_reply})
        
    except Exception as e:
        print(f"❌ Connection error interacting with the AI processing node: {e}")
        if "400" in str(e):
            print("⚠️ [Self-Healing] Broken tool sequence detected. Resetting chat history to clear the lock...")
            conversation_history = list(DEFAULT_SYSTEM_PROMPT)
            with open(MEMORY_FILE, "w") as f:
                json.dump(conversation_history, f)
            print("✅ History cleaned successfully. Please try your message again!\n")
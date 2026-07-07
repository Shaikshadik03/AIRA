import os
import json
import webbrowser  # Added for V4: Native tool use to open browser windows
from datetime import datetime  # Added for V4: Native tool use to access system clock
from dotenv import load_dotenv
from groq import Groq
from ddgs import DDGS      # Preserved V3: DuckDuckGo Search Engine
from pypdf import PdfReader  # Preserved V3: PDF Reader Document Extractor

# Load environment variables from your .env file
load_dotenv()

# Initialize the Groq cloud communication client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# =====================================================================
# 🚀 AIRA V4 SYSTEM — AGENT ACTION TOOL CORES
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
        # os.listdir(".") scans the current active workspace directory folder
        files = os.listdir(".")
        if not files:
            return "System message: The current directory workspace folder is entirely empty."
        
        # Turn the Python array into a clean string layout using newline joins
        bulleted_files = "\n".join([f"- {item}" for item in files])
        return f"System message: Here are the active workspace files found:\n{bulleted_files}"
    except Exception as e:
        return f"System Error: Unable to scan file system profile. Reason: {e}"


# 2. Scalable Tool Registry Directory Mapping
tool_registry = {
    "open_website": open_website,
    "get_current_time": get_current_time,
    "get_current_date": get_current_date,
    "list_files": list_files  # Newly registered file scanning capability pointer!
}

# 3. Dynamic Native AI Agent Tool Blueprints (JSON Schema Toolbox Array)
aira_tools = [
    {
        "type": "function",
        "function": {
            "name": "open_website",
            "description": "Opens any web URL in the browser. Use this whenever the user asks to open or navigate to a website (e.g., YouTube, Google, GitHub).",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The web URL string to open. Example: 'https://www.youtube.com'"
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Returns the current local real-world time. Use this whenever the user explicitly asks for the time, clock status, or what time it is.",
            "parameters": {
                "type": "object",
                "properties": {},  
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "Returns the current local real-world date. Use this whenever the user explicitly asks for today's date, what day it is, or calendar status.",
            "parameters": {
                "type": "object",
                "properties": {},  
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Lists all file documents and folders inside the current project workspace directory. Use this when the user asks to see what files exist, what is in the folder, or to view workspace contents.",
            "parameters": {
                "type": "object",
                "properties": {},  # Empty because it requires no extra text entries to read a local folder!
                "required": []
            }
        }
    }
]

# =====================================================================
# 🌐 AIRA V3 SYSTEM — CONTEXT EXTRACTION HELPER FUNCTIONS
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

def search_web(query: str) -> str:
    """Executes a text query search via DuckDuckGo and gathers summaries."""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=3)]
            search_text = ""
            for r in results:
                search_text += f"Title: {r['title']}\nSnippet: {r['body']}\n\n"
            return search_text
    except Exception as e:
        return f"System Error: Failed to fetch search results. Reason: {e}"

# =====================================================================
# 💾 AIRA V2 SYSTEM — PERSISTENT STORAGE MEMORY LOADER
# =====================================================================
MEMORY_FILE = "memory.json"

DEFAULT_SYSTEM_PROMPT = [
    {
        "role": "system", 
        "content": (
            "You are AIRA, a highly professional AI agent designed by Shadik. "
            "Respond directly and clearly. When calling tools, strictly output function "
            "formats without altering formatting or tags."
        )
    }
]

if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        try:
            conversation_history = json.load(f)
            print("🤖 Loaded previous memory layout successfully!\n")
        except Exception:
            conversation_history = list(DEFAULT_SYSTEM_PROMPT)
            print("⚠️ Memory file was unreadable. Started with fresh profile.\n")
else:
    conversation_history = list(DEFAULT_SYSTEM_PROMPT)

print("⚡ AIRA is online and running! Type 'exit' to cleanly close down.")
print("🌐 Format web search inquiries as: 'search: your question'")
print("📄 Format PDF document readings as: 'pdf: filename.pdf'\n")

# =====================================================================
# 💬 AIRA V1 SYSTEM — INTERACTIVE MAIN LOOP
# =====================================================================
while True:
    user_input = input("You: ").strip()
    
    if user_input.lower() == "exit":
        print("💾 Saving conversation logs securely to disk... Goodbye Shadik!")
        with open(MEMORY_FILE, "w") as f:
            json.dump(conversation_history, f)
        break

    if not user_input:
        continue

    # --- V3 WEB SEARCH INJECTION PATH ---
    if user_input.startswith("search:"):
        query = user_input[7:].strip()
        print(f"🔍 Contacting search servers for: '{query}'...")
        context_data = search_web(query)
        prompt_with_context = f"You are AIRA.\nBelow are live web search results.\n\n{context_data}\n\nUsing this information, answer the question: {query}"
        conversation_history.append({"role": "user", "content": prompt_with_context})

    # --- V3 PDF DOCUMENT INJECTION PATH ---
    elif user_input.startswith("pdf:"):
        file_name = user_input[4:].strip()
        print(f"📄 Scraping text content out of target document: '{file_name}'...")
        pdf_extracted_text = read_pdf(file_name)
        prompt_with_context = f"Here is the PDF content from file '{file_name}':\n\n{pdf_extracted_text}\n\nAnalyze and break down this data concisely for the user."
        conversation_history.append({"role": "user", "content": prompt_with_context})

    # --- V1 NORMAL STANDALONE CHAT PATH ---
    else:
        conversation_history.append({"role": "user", "content": user_input})

    # Transmit conversation logs out to the Groq API Engine
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=conversation_history,
            tools=aira_tools,        
            tool_choice="auto"       
        )
        
        message = response.choices[0].message
        
        # Checking if Groq successfully parsed a tool request
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
                model="llama-3.3-70b-versatile",
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
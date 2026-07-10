import sys
try:
    import pyaudiowpatch as pyaudio
    sys.modules['pyaudio'] = pyaudio
except ImportError: pass

# --- IMPORT LOCAL HARDWARE HOOKS FROM WORKSPACE ---
import database
from system_control import SystemController
from profile_manager import ProfileManager
from app_launcher import AppLauncher
from note_manager import NoteManager
# --------------------------------------------------

import asyncio
import websockets
import json
import psutil
import webbrowser
import pyttsx3

sys_control = SystemController()
launcher = AppLauncher()
profile_mgr = ProfileManager()
note_mgr = NoteManager("aira_notes.txt")

def speak_out_loud(text: str):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 180)
        engine.say(text.replace("**", ""))
        engine.runAndWait()
    except Exception: pass

async def local_agent_execution_loop():
    # Local connection targeting target runtime port (Change to cloud URL during final deployment)
    uri = "ws://localhost:8000/ws/agent"
    print(f"📡 [Local Agent] Activating transmission array targeting core node: {uri}")
    
    while True:
        try:
            async with websockets.connect(uri, ping_interval=20, ping_timeout=20) as websocket:
                print("🟢 [Connected] Secure hardware tunnel link established successfully.")
                speak_out_loud("Hardware daemon connection synchronized cleanly, Shadik.")
                
                while True:
                    message_bytes = await websocket.recv()
                    payload = json.loads(message_bytes)
                    
                    cmd_id = payload.get("id")
                    action_cmd = payload.get("action", "")
                    print(f"📥 [Inbound Command] ID: {cmd_id} | Action parameters: '{action_cmd}'")
                    
                    result_report = "Command initialized."
                    
                    # Intercept processing blocks mapped locally
                    if "system status" in action_cmd:
                        cpu = psutil.cpu_percent()
                        ram = psutil.virtual_memory().percent
                        result_report = f"📊 **Diagnostic Performance Matrix:**\n\n💻 CPU Load: {cpu}%\n🧠 RAM Allocation: {ram}%"
                        speak_out_loud(f"System status checked. CPU load is at {cpu} percent.")
                        
                    elif "lock" in action_cmd and "pc" in action_cmd:
                        res = sys_control.execute_action("lock")
                        result_report = f"🔒 OS Control Engine: {res}"
                        speak_out_loud("Locking computer terminal.")
                        
                    elif "sleep" in action_cmd:
                        res = sys_control.execute_action("sleep")
                        result_report = f"💤 OS Control Engine: {res}"
                        
                    elif "open" in action_cmd:
                        for app in ["chrome", "notepad", "vstext"]:
                            if app in action_cmd:
                                launcher.launch_program(app)
                                result_report = f"🚀 Launched application instance: {app.upper()}"
                                speak_out_loud(f"Opening {app} program loop.")
                                
                    # Return calculated hardware status indicators back up to the cloud gate
                    await websocket.send(json.dumps({
                        "id": cmd_id,
                        "result": result_report
                    }))
                    print(f"📤 [Outbound Response] Returned calculation results for package payload ID: {cmd_id}")
                    
        except (websockets.exceptions.ConnectionClosed, OSError):
            print("❌ [Disconnected] Connection link broken. Retrying handshake in 4 seconds...")
            await asyncio.sleep(4)
        except Exception as e:
            print(f"⚠️ [Runtime Warning] Unexpected matrix fault: {str(e)}")
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(local_agent_execution_loop())
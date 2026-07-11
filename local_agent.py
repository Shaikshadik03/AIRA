import os
import sys
import time
import json
import asyncio
import websockets
import pyautogui
import pyttsx3

# Initialize voice engine for hardware confirmations
try:
    engine = pyttsx3.init()
except Exception:
    engine = None

def speak(text):
    print(f"🔊 [Agent Voice]: {text}")
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass

RENDER_WS_URL = "wss://aira-l1c5.onrender.com/ws/agent"

async def run_hardware_agent():
    speak("Initializing secure connection framework to AIRA cloud core cluster.")
    
    while True:
        try:
            print(f"📡 Attempting connection to global grid: {RENDER_WS_URL}")
            async with websockets.connect(RENDER_WS_URL) as websocket:
                speak("AIRA Matrix online. Operational link established successfully.")
                print("✅ Secure reverse tunnel active. Listening for cloud directives...")
                
                while True:
                    message = await websocket.recv()
                    payload = json.loads(message)
                    cmd_id = payload.get("id")
                    action = payload.get("action", "").lower().strip()
                    
                    print(f"📥 Received execution frame [{cmd_id}]: {action}")
                    result_string = "Command unmapped."

                    try:
                        # 🛡️ SYSTEM STATUS DIRECTIVES
                        if "system status" in action:
                            result_string = "🖥️ **Laptop Status:** Online, connected to cloud matrix, power grid stable."
                        
                        # 🔒 SECURITY DIRECTIVES
                        elif "lock" in action:
                            speak("Securing console layer.")
                            if sys.platform == "win32":
                                os.system("rundll32.exe user32.dll,LockWorkStation")
                                result_string = "🔒 Command executed: Console interface locked securely."
                            else:
                                result_string = "⚠️ OS lock target not supported natively."
                                
                        elif "sleep" in action:
                            speak("Entering power suspension mode.")
                            if sys.platform == "win32":
                                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                                result_string = "🌙 Command executed: Laptop suspension mode engaged."
                            else:
                                result_string = "⚠️ OS sleep target not supported natively."

                        # 🌐 APPLICATION LAUNCH DIRECTIVES
                        elif "open chrome" in action:
                            speak("Launching internet browser.")
                            os.system("start chrome")
                            result_string = "🌐 Google Chrome initialized successfully."
                            
                        elif "open notepad" in action:
                            speak("Launching notepad core.")
                            os.system("start notepad")
                            result_string = "📝 Notepad instance launched successfully."
                            
                        elif "open vscode" in action or "open vs code" in action:
                            speak("Launching development workspace.")
                            os.system("code")
                            result_string = "💻 Visual Studio Code environment initialized."

                        # 🔊 NEW HARDWARE ENTERTAINMENT CONTROLS
                        elif "volume up" in action:
                            for _ in range(5):
                                pyautogui.press("volumeup")
                            result_string = "🔊 System volume increased by 5 units."

                        elif "volume down" in action:
                            for _ in range(5):
                                pyautogui.press("volumedown")
                            result_string = "🔉 System volume decreased by 5 units."

                        elif "mute" in action:
                            pyautogui.press("volumemute")
                            result_string = "🔇 System audio toggle executed successfully."

                        elif "play" in action or "pause" in action:
                            pyautogui.press("playpause")
                            result_string = "⏯️ Media playback state toggled."
                            
                        else:
                            result_string = f"❓ Operational command '{action}' not recognized by local agent."
                            
                    except Exception as error:
                        result_string = f"❌ Execution failure on laptop agent: {str(error)}"

                    # Send back response loop to cloud server
                    await websocket.send(json.dumps({"id": cmd_id, "result": result_string}))
                    print(f"📤 Transmission return loop completed for task [{cmd_id}].")

        except Exception as conn_error:
            print(f"⚠️ Link connection dropped or failed: {str(conn_error)}")
            print("⏳ Re-establishing transport protocol layer in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(run_hardware_agent())
    except KeyboardInterrupt:
        print("\n🛑 Laptop hardware agent shut down manually.")
import os
import sys
import time
import json
import asyncio
import websockets
import pyttsx3
import ctypes
import webbrowser
import pyautogui
import urllib.parse
import io
import base64
from PIL import Image
from datetime import datetime  # 🕒 Added to track exact time signatures

# 🔑 Windows Driver Core Virtual Key Map Codes
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_PLAY_PAUSE = 0xB3

def send_windows_hardware_key(vk_code):
    """Sends a raw hardware-level key event directly into the Windows OS kernel"""
    ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)      # Key Down (Press)
    time.sleep(0.05)                                     
    # Hold briefly
    ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0)      # Key Up (Release)

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
                    
                    # Core Response Architecture Structures
                    result_text = "Command unmapped."
                    result_image = None

                    try:
                        # 🛡️ SYSTEM STATUS DIRECTIVES
                        if "system status" in action:
                            result_text = "🖥️ **Laptop Status:** Online, connected to cloud matrix, power grid stable."
                        
                        # 🔒 SECURITY DIRECTIVES
                        elif "lock" in action:
                            speak("Securing console layer.")
                            if sys.platform == "win32":
                                os.system("rundll32.exe user32.dll,LockWorkStation")
                                result_text = "🔒 Command executed: Console interface locked securely."
                            else:
                                result_text = "⚠️ OS lock target not supported natively."
                                
                        elif "sleep" in action:
                            speak("Entering power suspension mode.")
                            if sys.platform == "win32":
                                # Package baseline parameters early for quick suspension flush
                                early_reply = {"text": "🌙 Command executed: Laptop suspension mode engaged.", "image": None}
                                await websocket.send(json.dumps({"id": cmd_id, "result": early_reply}))
                                print(f"📤 Transmission return loop completed early for sleep state.")
                                time.sleep(1.5)
                                os.system('powershell -command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState([System.Windows.Forms.PowerState]::Suspend, $false, $false)"')
                                continue
                            else:
                                result_text = "⚠️ OS sleep target not supported natively."

                        # 🔍 NEW DYNAMIC SEARCH ENGINE DIRECTIVE
                        elif action.startswith("search"):
                            search_query = action.replace("search", "", 1).strip()
                            if search_query:
                                speak(f"Executing deep web search grid query for {search_query}")
                                encoded_query = urllib.parse.quote(search_query)
                                search_url = f"https://www.google.com/search?q={encoded_query}"
                                webbrowser.open(search_url)
                                result_text = f"🔍 **Search Active:** Default browser routed to Google for query: `{search_query}`"
                            else:
                                result_text = "⚠️ **Search Error:** Empty query string detected. Try typing: `search [your topic]`"

                        # 🌐 NATIVE APPLICATION LAUNCH DIRECTIVES
                        elif "open chrome" in action:
                            speak("Launching internet browser.")
                            os.system("start chrome")
                            result_text = "🌐 Google Chrome initialized successfully."
                            
                        elif "open notepad" in action:
                            speak("Launching notepad core.")
                            os.system("start notepad")
                            result_text = "📝 Notepad instance launched successfully."
                            
                        elif "open vscode" in action or "open vs code" in action:
                            speak("Launching development workspace.")
                            os.system("code")
                            result_text = "💻 Visual Studio Code environment initialized."

                        # 🔗 GLOBAL WEBSITE URL LAUNCH DIRECTIVES
                        elif "open youtube" in action:
                            speak("Opening YouTube.")
                            webbrowser.open("https://www.youtube.com")
                            result_text = "📺 YouTube pipeline opened in your default browser."
                            
                        elif "open github" in action:
                            speak("Opening GitHub.")
                            webbrowser.open("https://www.github.com")
                            result_text = "🐙 GitHub code portal opened in your default browser."
                            
                        elif "open leetcode" in action:
                            speak("Opening LeetCode.")
                            webbrowser.open("https://www.leetcode.com")
                            result_text = "🧠 LeetCode automation panel ready for algorithms."
                            
                        elif "open google" in action:
                            speak("Opening Google search.")
                            webbrowser.open("https://www.google.com")
                            result_text = "🔍 Google Search opened in your default browser."

                        # 🔊 CORE WINDOWS DRIVER AUDIO CONTROLS
                        elif "volume up" in action:
                            for _ in range(5):
                                send_windows_hardware_key(VK_VOLUME_UP)
                                time.sleep(0.02)
                            result_text = "🔊 System volume increased by 5 units via hardware kernel."

                        elif "volume down" in action:
                            for _ in range(5):
                                send_windows_hardware_key(VK_VOLUME_DOWN)
                                time.sleep(0.02)
                            result_text = "🔉 System volume decreased by 5 units via hardware kernel."

                        elif "mute" in action:
                            send_windows_hardware_key(VK_VOLUME_MUTE)
                            result_text = "🔇 System audio mute state toggled via hardware kernel."

                        elif "play" in action or "pause" in action:
                            send_windows_hardware_key(VK_MEDIA_PLAY_PAUSE)
                            result_text = "⏯️ Media playback state toggled via hardware kernel."

                        # 📸 REVERSE SCREENSHOT STREAM DIRECTIVE
                        elif "screenshot" in action or "capture screen" in action:
                            speak("Capturing screen array map.")
                            
                            # ⚡ UPGRADED: Create a completely unique name using the current date and time
                            timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
                            ss_filename = f"aira_snap_{timestamp}.png"
                            
                            try:
                                pyautogui.screenshot(ss_filename)
                                abs_path = os.path.abspath(ss_filename)
                                
                                # ⚡ COMPRESSION PIPELINE: Read, downscale, and convert to light buffer stream
                                with Image.open(ss_filename) as img:
                                    img.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
                                    buffer = io.BytesIO()
                                    img.convert("RGB").save(buffer, format="JPEG", quality=60)
                                    result_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
                                
                                result_text = f"📸 **Snapshot Captured:** Saved locally at `{abs_path}`"
                            except Exception as inside_err:
                                result_text = f"❌ **Screenshot Error:** Display grid captured, but compression framework failed: {str(inside_err)}"
                            
                        else:
                            result_text = f"❓ Operational command '{action}' not recognized by local agent."
                            
                    except Exception as error:
                        result_text = f"❌ Execution failure on laptop agent: {str(error)}"

                    # Send back response object containing separated data mappings
                    response_payload = {"text": result_text, "image": result_image}
                    await websocket.send(json.dumps({"id": cmd_id, "result": response_payload}))
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
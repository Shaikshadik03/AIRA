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

# 🔑 Windows Driver Core Virtual Key Map Codes
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_PLAY_PAUSE = 0xB3

def send_windows_hardware_key(vk_code):
    """Sends a raw hardware-level key event directly into the Windows OS kernel"""
    ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)      # Key Down (Press)
    time.sleep(0.05)                                        # Hold briefly
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

                        # 🌐 NATIVE APPLICATION LAUNCH DIRECTIVES
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

                        # 🔗 NEW GLOBAL WEBSITE URL LAUNCH DIRECTIVES
                        elif "open youtube" in action:
                            speak("Opening YouTube.")
                            webbrowser.open("https://www.youtube.com")
                            result_string = "📺 YouTube pipeline opened in your default browser."
                            
                        elif "open github" in action:
                            speak("Opening GitHub.")
                            webbrowser.open("https://www.github.com")
                            result_string = "🐙 GitHub code portal opened in your default browser."
                            
                        elif "open leetcode" in action:
                            speak("Opening LeetCode.")
                            webbrowser.open("https://www.leetcode.com")
                            result_string = "🧠 LeetCode automation panel ready for algorithms."
                            
                        elif "open google" in action:
                            speak("Opening Google search.")
                            webbrowser.open("https://www.google.com")
                            result_string = "🔍 Google Search opened in your default browser."

                        # 🔊 CORE WINDOWS DRIVER AUDIO CONTROLS
                        elif "volume up" in action:
                            for _ in range(5):
                                send_windows_hardware_key(VK_VOLUME_UP)
                                time.sleep(0.02)
                            result_string = "🔊 System volume increased by 5 units via hardware kernel."

                        elif "volume down" in action:
                            for _ in range(5):
                                send_windows_hardware_key(VK_VOLUME_DOWN)
                                time.sleep(0.02)
                            result_string = "🔉 System volume decreased by 5 units via hardware kernel."

                        elif "mute" in action:
                            send_windows_hardware_key(VK_VOLUME_MUTE)
                            result_string = "🔇 System audio mute state toggled via hardware kernel."

                        elif "play" in action or "pause" in action:
                            send_windows_hardware_key(VK_MEDIA_PLAY_PAUSE)
                            result_string = "⏯️ Media playback state toggled via hardware kernel."

                        # 📸 NEW REVERSE SCREENSHOT STREAM DIRECTIVE
                        elif "screenshot" in action or "capture screen" in action:
                            speak("Capturing screen array map.")
                            ss_filename = "aira_desktop_snap.png"
                            pyautogui.screenshot(ss_filename)
                            # Finds absolute storage address path
                            abs_path = os.path.abspath(ss_filename)
                            result_string = f"📸 **Snapshot Captured:** Desktop image successfully mapped and saved locally at: `{abs_path}`"
                            
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
import subprocess
import os
import sys

class AppLauncher:
    def __init__(self):
        """Initializes the registry of applications on your laptop."""
        # This dictionary maps simple shortcut nicknames to their real path on your PC
        self.app_registry = {
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "notepad": "notepad.exe", # Windows knows where notepad is automatically
            "vstext": r"C:\Users\arsha\AppData\Local\Programs\Microsoft VS Code\Code.exe" 
        }
        print("[AIRA APPS] Application registry loaded mapping channels.")

    def launch_program(self, app_alias: str) -> str:
        """Attempts to open a specific application natively on your computer layout."""
        app_name = app_alias.lower().strip()
        
        # Check if the nickname exists in our dictionary
        if app_name in self.app_registry:
            target_path = self.app_registry[app_name]
            try:
                # subprocess.Popen runs the app in the background so it doesn't freeze Python
                subprocess.Popen(target_path)
                return f"🚀 Rocket engines engaged: Successfully launched {app_name.upper()}."
            except Exception as e:
                return f"❌ Failed to boot core path for {app_name}: {str(e)}"
        else:
            return f"⚠️ App link '{app_name}' not found in registry. Add its file path to app_launcher.py!"
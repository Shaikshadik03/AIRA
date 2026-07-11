import os
import sys

class SystemController:
    def __init__(self):
        # This checks if your laptop is running Windows or Mac
        self.platform = sys.platform
        print(f"[AIRA OS] System Controller initialized for platform: {self.platform}")

    def execute_action(self, action: str, target_value=None) -> str:
        """Routes the string command to the correct system function."""
        action = action.lower().strip()
        
        if action == "lock":
            return self.lock_screen()
        elif action == "sleep":
            return self.sleep_pc()
        elif action == "volume":
            return self.set_volume(target_value)
        else:
            return f"Error: Command '{action}' not found."

    def lock_screen(self) -> str:
        """Locks your Windows computer screen."""
        if self.platform == "win32":
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "Windows workstation locked successfully."
        return "Lock screen hook is only configured for Windows right now."

    def sleep_pc(self) -> str:
        """Puts your Windows computer to sleep."""
        if self.platform == "win32":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "Windows system entering sleep mode."
        return "Sleep hook is only configured for Windows right now."

    def set_volume(self, level) -> str:
        """Placeholder for volume adjustment logic."""
        if level is None:
            return "Error: Missing volume level parameter."
        return f"Windows volume change request received for {level}%."
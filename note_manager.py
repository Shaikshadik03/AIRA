import os

class NoteManager:
    def __init__(self, filename: str = "aira_notes.txt"):
        """Initializes the text note tracker module."""
        self.filename = filename

    def write_note(self, note_text: str) -> str:
        """Appends a fresh line of text into your local workspace note file."""
        try:
            with open(self.filename, "a", encoding="utf-8") as file:
                file.write(f"- {note_text}\n")
            return f"📝 Note logged successfully into '{self.filename}'."
        except Exception as e:
            return f"❌ Failed to write file cluster: {str(e)}"

    def read_notes(self) -> str:
        """Reads your entire text file notes and returns them neatly formatted."""
        if not os.path.exists(self.filename):
            return "📝 Workspace log is empty. No notes have been created yet, Shadik."
            
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                lines = file.readlines()
                
            if not lines:
                return "📝 Workspace log is empty. No notes found inside the text file."
                
            summary = "📋 **Current AIRA Workspace Notes:**\n\n"
            for line in lines:
                summary += line
            return summary
        except Exception as e:
            return f"❌ Failed to extract note clusters: {str(e)}"
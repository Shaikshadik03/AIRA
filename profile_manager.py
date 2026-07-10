import sqlite3

DB_NAME = "aira_cloud_node.db"

class ProfileManager:
    def __init__(self):
        """Initializes the profile manager cluster."""
        pass

    def remember_user_fact(self, category: str, fact: str, importance: int = 3):
        """Saves a unique personal fact about you into AIRA's long-term memory database."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO memory_nodes (category, fact_content, importance_score) VALUES (?, ?, ?)",
            (category.strip().lower(), fact.strip(), importance)
        )
        
        conn.commit()
        conn.close()
        return f"🧠 Memory locked into clusters: Added '{fact}' under '{category}'."

    def pull_all_memories(self) -> str:
        """Gathers every saved fact about you so the AI can read it for context."""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("SELECT category, fact_content FROM memory_nodes ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return "No personal user data currently indexed in memory clusters."
            
        # Formats the facts into a clean text block for the AI
        memory_summary = "\n--- EXTENDED USER MEMORY PROFILE ---\n"
        for category, fact in rows:
            memory_summary += f"• [{category.upper()}]: {fact}\n"
        memory_summary += "------------------------------------"
        
        return memory_summary
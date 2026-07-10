import sqlite3

DB_NAME = "aira_cloud_node.db"

def init_db():
    """Creates the local database tables if they do not exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create memory nodes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory_nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            fact_content TEXT NOT NULL,
            importance_score INTEGER DEFAULT 1,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create interaction metrics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interaction_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command_executed TEXT NOT NULL,
            module_used TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("[AIRA DB] Database and tables are ready to use!")

def log_interaction_metric(command: str, module: str):
    """Logs executed commands into the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO interaction_metrics (command_executed, module_used) VALUES (?, ?)",
        (command, module)
    )
    conn.commit()
    conn.close()
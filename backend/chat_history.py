import sqlite3

def put_chat_history(thread_id: str, role: int, response: str, status: int):
    """Store a message in the chat history for a specific thread."""
    conn = sqlite3.connect(f"agent_chat.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id TEXT NOT NULL,
            role INTEGER NOT NULL,
            response TEXT NOT NULL,
            status INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("INSERT INTO chat_history (thread_id,role, response,status) VALUES (?,?, ?,?)", (thread_id,role, response, status))
    conn.commit()
    conn.close()

def get_chat_history(thread_id: str, page: int = 1, page_size: int = 20):
    """Retrieve chat history for a specific thread with pagination."""
    conn = sqlite3.connect(f"agent_chat.db")
    cursor = conn.cursor()
    offset = (page - 1) * page_size
    cursor.execute("SELECT role, response, status, timestamp FROM chat_history WHERE thread_id = ? ORDER BY timestamp DESC LIMIT ? OFFSET ?", (thread_id, page_size, offset))
    history = cursor.fetchall()
    conn.close()
    return history
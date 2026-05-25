import sqlite3

def get_chat_tables(threadId: str):
    conn = sqlite3.connect(f"agent_{threadId}.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table';
    """)

    tables = cursor.fetchall()
    table_schema = []

    tables_res = [ t[0] for t in tables ]

    conn.close()
    return tables_res

def get_chat_table_schema(threadId: str, table_name: str):
    conn = sqlite3.connect(f"agent_{threadId}.db")

    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    columns_filter = [[col[1],col[2]] for col in columns]

    cursor.execute(f"SELECT * FROM {table_name};")
    data = cursor.fetchall()
    conn.close()
    return {
        "columns": columns_filter,
        "data": data
    }
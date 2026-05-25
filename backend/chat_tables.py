import sqllite3

def get_chat_tables(threadId: str):
    conn = sqllite3.connect(f"agent_${threadId}.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table';
    """)

    tables = cursor.fetchall()
    table_schema = []

    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()

        column_info = ", ".join(
            [f"{col[1]} ({col[2]})" for col in columns]
        )

        table_schema.append(f"Table: {table_name}, Columns: {column_info}")

    conn.close()
    return "\n".join(table_schema) if table_schema else "No tables found."
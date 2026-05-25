import sqlite3
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool


def split_sql_statements(sql: str) -> list[str]:
    statements = []
    current = []
    quote = None
    escaped = False

    for char in sql:
        current.append(char)

        if quote:
            if char == quote and not escaped:
                quote = None
            escaped = char == "\\" and not escaped
            if char != "\\":
                escaped = False
            continue

        if char in ("'", '"'):
            quote = char
            continue

        if char == ";":
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []

    statement = "".join(current).strip()
    if statement:
        statements.append(statement)

    return statements


@tool
def execute_sql(sql: str, config: RunnableConfig) -> str:
    """Execute the provided SQL statement and return results."""
    thread_id = config["configurable"]["thread_id"]
    print(f"DEBUG: execute_sql tool called for thread_id {thread_id} with SQL: {sql}")
    statements = split_sql_statements(sql)

    if not statements:
        return "SQL execution error: no SQL statement provided."

    try:
        conn = sqlite3.connect(f"agent_{thread_id}.db")  # Use thread-specific database
        cursor = conn.cursor()
        results = []

        for statement in statements:
            cursor.execute(statement)
            if statement.strip().lower().startswith("select"):
                results.append(cursor.fetchall())

        conn.commit()
        conn.close()

        if results:
            print(f"DEBUG: SQL execution results: {results[-1]}")
            return f"Query Results: {results[-1]}"

        return "SQL executed successfully."
    except Exception as e:
        return f"SQL execution error: {e}"
    
def is_safe_sql(sql: str) -> bool:
    blocked = ["drop table", "drop database", "truncate", "pragma", "attach", "detach"]
    statements = split_sql_statements(sql)

    if not statements:
        return False

    for statement in statements:
        sql_lower = statement.strip().lower()

        if any(word in sql_lower for word in blocked):
            return False

        if sql_lower.startswith("delete") and "where" not in sql_lower:
            return False

        if not sql_lower.startswith(("select", "insert", "update", "delete", "create", "alter")):
            return False

    return True


import sqlite3
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, AnyMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool


@tool
def execute_sql(sql: str, config: RunnableConfig) -> str:
    """Execute the provided SQL statement and return results."""
    thread_id = config["configurable"]["thread_id"]
    print(f"DEBUG: execute_sql tool called with SQL: {thread_id}")
    try:
        conn = sqlite3.connect(f"agent_{thread_id}.db")  # Use thread-specific database
        cursor = conn.cursor()


        cursor.execute(sql)
        conn.commit()
        if sql.strip().lower().startswith("select"):
            results = cursor.fetchall()
            return f"Query Results: {results}"
        conn.close()
        return "SQL executed successfully."
    except Exception as e:
        return f"SQL execution error: {e}"
    
def is_safe_sql(sql: str) -> bool:
    sql_lower = sql.strip().lower()

    blocked = ["drop table", "drop database", "truncate", "pragma", "attach", "detach"]

    if any(word in sql_lower for word in blocked):
        return False

    if sql_lower.startswith("delete") and "where" not in sql_lower:
        return False

    return sql_lower.startswith(("select", "insert", "update", "delete", "create", "alter"))


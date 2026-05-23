import os
import sys
from tkinter import Image

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig

from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.types import interrupt
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.types import Interrupt


from models.adovcator import advocator_prompt, llm
from models.analyzer import analyzer_prompt
from agent_class import GraphState
import sqlite3


def pretty_print_event(event):

    # Handle interrupt events
    if "__interrupt__" in event:
        interrupts = event["__interrupt__"]

        for intr in interrupts:
            if hasattr(intr, "value"):
                query = intr.value.get("query", "Human assistance required.")
                print(f"\n[HUMAN ASSISTANCE REQUIRED]")
                print(f"Agent Question: {query}\n")

        return

    # Handle normal node events
    for node_name, value in event.items():

        if not isinstance(value, dict):
            continue

        messages = value.get("messages", [])

        if not messages:
            continue

        last_message = messages[-1]

        # Human messages
        if isinstance(last_message, HumanMessage):
            print(f"\n[USER]")
            print(last_message.content)

        # AI messages
        elif isinstance(last_message, AIMessage):

            # Tool calls
            if getattr(last_message, "tool_calls", None):

                for tool_call in last_message.tool_calls:
                    tool_name = tool_call["name"]

                    print(f"\n[{node_name.upper()} TOOL CALL]")
                    print(f"Tool: {tool_name}")

                    if "args" in tool_call:
                        print(f"Arguments: {tool_call['args']}")

            # Normal AI response
            elif last_message.content.strip():

                print(f"\n[{node_name.upper()}]")
                print(last_message.content)

        # Tool messages
        elif isinstance(last_message, ToolMessage):

            print(f"\n[TOOL RESULT]")
            print(last_message.content)

@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    human_response = interrupt({"query": query})
    return human_response["data"]

@tool
def get_sql_schema(config: RunnableConfig) -> str:
    """Return the current SQLite database schema. Takes no arguments."""

    thread_id = config["configurable"]["thread_id"]
    print(f"DEBUG: get_sql_schema called for thread_id: {thread_id}")
    conn = sqlite3.connect(f"agent_{thread_id}.db")
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

memory = InMemorySaver()
config = {"configurable": {"thread_id": "1"}}
advocator_tools = [human_assistance, get_sql_schema]
analyzer_tools = [execute_sql]

adv_llm_with_tools = llm.bind_tools(advocator_tools)
ana_llm_with_tools = llm.bind_tools(analyzer_tools)
llm_advocator = advocator_prompt | adv_llm_with_tools
llm_analyzer_with_tools = analyzer_prompt | ana_llm_with_tools

def route_from_creator(state):
    last = state["messages"][-1]

    if getattr(last, "tool_calls", None):
        return "creator_tools"

    content = last.content.strip()

    print("DEBUG ROUTER CONTENT:", content)


    if content.startswith("Capable of generating SQL statements only"):
        return END

    if "?" in content:
        return END

    if not content.lower().startswith(("select", "insert", "update", "delete", "create", "alter", "drop")):
        print("DEBUG: Content does not appear to be SQL, ending graph.")
        return END
    print("DEBUG: passing to node_b")

    return "node_b"

def is_safe_sql(sql: str) -> bool:
    sql_lower = sql.strip().lower()

    blocked = ["drop table", "drop database", "truncate", "pragma", "attach", "detach"]

    if any(word in sql_lower for word in blocked):
        return False

    if sql_lower.startswith("delete") and "where" not in sql_lower:
        return False

    return sql_lower.startswith(("select", "insert", "update", "delete", "create", "alter"))


def node_a(state: GraphState, config: RunnableConfig) -> GraphState:
    response = llm_advocator.invoke({"messages": state["messages"]}, config=config)
    return {
        "messages": [response]  # Wrap the response in a list to maintain consistency
    }


def node_b(state: GraphState, config: RunnableConfig) -> GraphState:
    sql = state["messages"][-1].content.strip()

    print("DEBUG: ENTERED NODE_B")
    print("DEBUG SQL TO REVIEW:", sql)

    if not is_safe_sql(sql):
        return {
            "messages": [AIMessage(content="It is not safe to execute this SQL statement.")]
        }

    result = execute_sql.invoke({"sql": sql}, config=config)

    return {
        "messages": [AIMessage(content=result)]
    }



def main():

    graph_builder = StateGraph(GraphState)
    graph_builder.add_node("node_a", node_a)
    graph_builder.add_node("node_b", node_b)
    advocator_tool_node = ToolNode(tools=advocator_tools)
    graph_builder.add_node("advocator_tools", advocator_tool_node)
    graph_builder.add_conditional_edges(
        "node_a",
        route_from_creator,
        {
            "creator_tools": "advocator_tools",
            "node_b": "node_b",
            END: END,
        }
    )

    graph_builder.add_edge("advocator_tools", "node_a")
    graph_builder.add_edge(START, "node_a")
    graph_builder.add_edge("node_b", END)

    graph = graph_builder.compile(checkpointer = memory)

    # png_data = graph.get_graph().draw_mermaid_png()

    # with open("graph.png", "wb") as f:
    #     f.write(png_data)
    # try:
    #     response = node_a({
    #         "name": "user",
    #         "messages": [HumanMessage(content="hi")]
    #     })
    #     # Print only the generated message text
    #     print("Advocator:", response["messages"][0].content)
    # except Exception as e:
    #     print(f"Error: {e}")

    # def stream_graph_updates(user_input: str):
    #     config = {"configurable": {"thread_id": "2"}}

    #     for event in graph.stream(
    #         {
    #             "name": "user",
    #             "messages": [HumanMessage(content=user_input)]
    #         },
    #         config=config
    #     ):
    #         pretty_print_event(event)


    # while True:
    #     try:
    #         user_input = input("User: ")
    #         if user_input.lower() in ["quit", "exit", "q"]:
    #             print("Goodbye!")
    #             break
    #         stream_graph_updates(user_input)
    #     except Exception as e:
    #         print("Goodbye!", e)
    #         break
    return graph

graph = main()
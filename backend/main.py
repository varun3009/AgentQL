from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt

from agent_class import GraphState

from tools.execute_sql import execute_sql, is_safe_sql
from tools.schema_tool import get_sql_schema

from models.general_chat import general_chain
from models.sql_generator import sql_gen_chain
from models.intent_router import intent_chain
from models.response_formatter import response_chain
from models.clarrifier import clarifier_chain


memory = InMemorySaver()


def intent_router_node(state: GraphState, config: RunnableConfig):
    response = intent_chain.invoke(
        {"messages": state["messages"]},
        config=config
    )

    # print(f"DEBUG: Intent router response: {response}")

    return {
        "intent": response.content if hasattr(response, "content") else str(response.route),
        "clarified": False,
        "sql": None,
        "is_safe": None,
        "execution_result": None,
    }


def route_from_intent(state: GraphState):

    print(f"DEBUG: Routing from intent: {state['intent']}")
    if state["intent"] == "general_chat":
        return "general_chat"

    if state["intent"] == "sql_request":
        return "schema_reader"
    print(f"did you go MF DEBUG: Routing from intent: {state['intent']}")

    return "general_chat"


def general_chat_node(state: GraphState, config: RunnableConfig):
    response = general_chain.invoke(
        {"messages": state["messages"]},
        config=config
    )
    print("DEBUG: Entering general_chat_node with messages:", response.content if hasattr(response, "content") else str(response))

    return {
        "messages": [AIMessage(content=response.content if hasattr(response, "content") else str(response))]
    }


def schema_reader_node(state: GraphState, config: RunnableConfig):
    schema = get_sql_schema.invoke({}, config=config)

    return {
        "schema": schema
    }


def clarifier_node(state: GraphState, config: RunnableConfig):
    response = clarifier_chain.invoke(
        {
            "messages": state["messages"],
            "schema": state.get("schema", "")
        },
        config=config
    )

    print(f"DEBUG: Clarifier response: {response}")

    if response.needs_clarification:
        human_response = interrupt({
            "query": response.question
        })

        return {
            "messages": [HumanMessage(content=human_response["data"])]
        }

    return {
        "clarified": True
    }

def route_from_clarifier(state):
    if state.get("clarified"):
        return "sql_generator"
    return "clarifier"

def sql_generator_node(state: GraphState, config: RunnableConfig):
    response = sql_gen_chain.invoke(
        {
            "messages": state["messages"],
            "schema": state.get("schema", "")
        },
        config=config
    )

    print(f"DEBUG: SQL Generator response: {response.content}")

    return {
        "sql": response.content
    }


def safety_checker_node(state: GraphState):
    sql = state["sql"]

    print(f"DEBUG: Checking safety of SQL: {sql}")
    if not is_safe_sql(sql):
        print(f"DEBUG: SQL is not safe: {sql}")
        return {
            "is_safe": False,
            "execution_result": "It is not safe to execute this SQL statement."
        }
    print(f"DEBUG: SQL is safe: {sql}")
    return {
        "is_safe": True
    }


def route_from_safety(state: GraphState):
    if state["is_safe"]:
        return "execute_sql"

    return "response_formatter"


def execute_sql_node(state: GraphState, config: RunnableConfig):
    result = execute_sql.invoke(
        {"sql": state["sql"]},
        config=config
    )

    print(f"DEBUG: SQL execution result: {result}")

    return {
        "execution_result": result
    }


def format_execution_error(execution_result: str) -> str | None:
    if not execution_result.startswith("SQL execution error:"):
        return None

    detail = execution_result.removeprefix("SQL execution error:").strip()
    detail_lower = detail.lower()

    if "already exists" in detail_lower:
        parts = detail.split()
        if len(parts) >= 4 and parts[0].lower() == "table":
            return f"I couldn't complete that because the {parts[1]} table already exists."
        return f"I couldn't complete that because {detail}."

    if detail_lower.startswith("no such table:"):
        table = detail.split(":", 1)[1].strip()
        return f"I couldn't complete that because the {table} table does not exist."

    if detail_lower.startswith("no such column:"):
        column = detail.split(":", 1)[1].strip()
        return f"I couldn't complete that because the {column} column does not exist."

    if "unique constraint failed:" in detail_lower:
        target = detail.split(":", 1)[1].strip()
        return f"I couldn't complete that because a row with that {target} value already exists."

    if "not null constraint failed:" in detail_lower:
        target = detail.split(":", 1)[1].strip()
        return f"I couldn't complete that because {target} cannot be empty."

    if "syntax error" in detail_lower:
        return "I couldn't complete that because the generated database command has a syntax error."

    return f"I couldn't complete that because the database returned this error: {detail}."


def response_formatter_node(state: GraphState, config: RunnableConfig):
    execution_result = state.get("execution_result", "")
    formatted_error = format_execution_error(execution_result)

    if formatted_error:
        return {
            "messages": [AIMessage(content=formatted_error)]
        }

    response = response_chain.invoke(
        {
            "messages": state["messages"],
            "schema": state.get("schema", ""),
            "sql": state.get("sql", ""),
            "execution_result": execution_result
        },
        config=config
    )

    return {
        "messages": [
            AIMessage(
                content=response.content if hasattr(response, "content") else str(response)
            )
        ]
    }


def build_graph():
    graph_builder = StateGraph(GraphState)

    graph_builder.add_node("intent_router", intent_router_node)
    graph_builder.add_node("general_chat", general_chat_node)
    graph_builder.add_node("schema_reader", schema_reader_node)
    graph_builder.add_node("clarifier", clarifier_node)
    graph_builder.add_node("sql_generator", sql_generator_node)
    graph_builder.add_node("safety_checker", safety_checker_node)
    graph_builder.add_node("execute_sql", execute_sql_node)
    graph_builder.add_node("response_formatter", response_formatter_node)

    graph_builder.add_edge(START, "intent_router")

    graph_builder.add_conditional_edges(
        "intent_router",
        route_from_intent,
        {
            "general_chat": "general_chat",
            "schema_reader": "schema_reader",
        }
    )

    graph_builder.add_edge("general_chat", END)

    graph_builder.add_edge("schema_reader", "clarifier")
    graph_builder.add_conditional_edges("clarifier",
        route_from_clarifier,
        {
            "clarifier": "clarifier",
            "sql_generator": "sql_generator"
        }
    )
    graph_builder.add_edge("sql_generator", "safety_checker")

    graph_builder.add_conditional_edges(
        "safety_checker",
        route_from_safety,
        {
            "execute_sql": "execute_sql",
            "response_formatter": "response_formatter",
        }
    )

    graph_builder.add_edge("execute_sql", "response_formatter")
    graph_builder.add_edge("response_formatter", END)

    return graph_builder.compile(checkpointer=memory)


graph = build_graph()

if __name__ == "__main__":
    png_data = graph.get_graph().draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(png_data)

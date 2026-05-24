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
        "intent": response.content if hasattr(response, "content") else str(response.route)
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

    if not is_safe_sql(sql):
        return {
            "is_safe": False,
            "execution_result": "It is not safe to execute this SQL statement."
        }

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

    return {
        "execution_result": result
    }


def response_formatter_node(state: GraphState, config: RunnableConfig):
    response = response_chain.invoke(
        {
            "messages": state["messages"],
            "schema": state.get("schema", ""),
            "sql": state.get("sql", ""),
            "execution_result": state.get("execution_result", "")
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
    graph_builder.add_edge("clarifier", "sql_generator")
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

png_data = graph.get_graph().draw_mermaid_png()
with open("graph.png", "wb") as f:
    f.write(png_data)
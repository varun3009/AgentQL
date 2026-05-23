from flask import Flask, request, jsonify
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.types import Command
import uuid
from main import graph
from enums.llm_status import LLMStatus, Role
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

def extract_response(events, thread_id=None):
    final_response = None

    for event in events:
        if "__interrupt__" in event:
            interrupt_obj = event["__interrupt__"][0]
            question = interrupt_obj.value.get("query", "Additional details required.")

            return {
                "role": Role.AGENT.value,
                "status": LLMStatus.INTERRUPT.value,
                "response": question,
                "thread_id": thread_id
            }

        for node_name, value in event.items():
            if not isinstance(value, dict):
                continue

            messages = value.get("messages", [])
            if not messages:
                continue

            last = messages[-1]

            if isinstance(last, AIMessage) and last.content.strip():
                final_response = last.content.strip()

            elif isinstance(last, ToolMessage):
                final_response = last.content.strip()

    return {
        "role": Role.AGENT.value,
        "status": LLMStatus.COMPLETED.value,
        "response": final_response,
        "thread_id": thread_id
    }


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    thread_id = data.get("thread_id") or str(uuid.uuid4())
    message = data.get("message")

    if not message:
        return jsonify({
            "error": "thread_id and message are required"
        }), 400

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    events = graph.stream(
        {
            "messages": [HumanMessage(content=message)]
        },
        config=config
    )

    return jsonify(extract_response(events, thread_id=thread_id))


@app.route("/resume", methods=["POST"])
def resume():
    data = request.get_json()

    thread_id = data.get("thread_id")
    answer = data.get("answer")

    if not thread_id or not answer:
        return jsonify({
            "error": "thread_id and answer are required"
        }), 400

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    events = graph.stream(
        Command(resume={"data": answer}),
        config=config
    )

    return jsonify(extract_response(events, thread_id=thread_id))


if __name__ == "__main__":
    app.run(debug=True, port=6969)
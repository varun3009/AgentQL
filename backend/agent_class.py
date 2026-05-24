from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing import Annotated, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from typing import Optional

class State(TypedDict):
    name: str

class GraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    intent: Optional[str]
    schema: Optional[str]
    clarified: Optional[bool]
    sql: Optional[str]
    is_safe: Optional[bool]
    execution_result: Optional[str]

class IntentResponse(BaseModel):
    route: Literal["general_chat", "sql_request"]

class ClarificationResponse(BaseModel):
    needs_clarification: bool
    question: Optional[str]
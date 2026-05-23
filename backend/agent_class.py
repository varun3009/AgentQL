from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing import Annotated
from typing_extensions import TypedDict

from pydantic import BaseModel, Field
from typing import Optional

class AdvocatorResponse(BaseModel):
    sqlstmt: Optional[str] = Field(None,description="The sql statement")
    is_end: bool = Field(description="Is sql statement generated or not")

class State(TypedDict):
    name: str

class GraphState(State) :
    messages: Annotated[list[AnyMessage], add_messages]
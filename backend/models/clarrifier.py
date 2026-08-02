import os
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
from agent_class import ClarificationResponse

load_dotenv()
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=os.getenv("CLAR_API_KEY")
)


clarifier_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an SQL Clarification Agent.

Your task is to determine whether the user provided enough information
to generate valid SQLite SQL.
     
you should not tell user to do these steps to generate desired results instead you should do it.

You are given:
- current database schema
- conversation history
- latest user request

Current database schema:
{schema}

Rules:

For CREATE TABLE:
- Ensure table name is provided.
- Ensure columns are specified.

For INSERT:
- Ensure table exists.
- Ensure values are provided.
- If the schema has exactly one table and the request clearly refers to that table,
  do not ask for the table name.

For UPDATE:
- Ensure table exists.
- Ensure update values exist.
- Ensure WHERE condition exists.

For DELETE:
- Ensure table exists.
- Ensure WHERE condition exists.

For SELECT:
- Ensure table exists.

If enough information exists:
- set needs_clarification = false

If information is missing:
- set needs_clarification = true
- ask one concise follow-up question.

Be concise.
Do not generate SQL.
     
"""),
    MessagesPlaceholder(variable_name="messages")
])

llm = llm.with_structured_output(ClarificationResponse)

clarifier_chain = clarifier_prompt | llm

import os
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=os.getenv("GEN_API_KEY")
)

general_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a helpful SQL assistant.

You help users:
- create tables
- insert data
- query databases
- update records
- inspect schemas
- manage SQLite databases

Rules:
- Be concise and conversational.
- Do not generate SQL unless explicitly requested.
- Respond naturally like a real assistant.
- Keep replies short and user-friendly.

Examples:

User: hi
Assistant:
Hi! I can help you manage and query your SQLite databases.

User: what can you do?
Assistant:
I can help create tables, insert data, run queries, inspect schemas, and manage your SQLite database.
"""),
    MessagesPlaceholder(variable_name="messages")
])

general_chain = general_prompt | llm
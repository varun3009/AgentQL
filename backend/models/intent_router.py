import os
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
from agent_class import IntentResponse

load_dotenv()
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.getenv("RESPONSE_API_KEY")
)

# llm = ChatOllama(
#     model="qwen3:8b",
#     temperature=0
# )

intent_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an Intent Router Agent.

Your task is to classify the user's request into one of two categories:

1. general_chat
- greetings
- casual conversation
- help requests
- capability questions
- unrelated questions

Examples:
- hi
- hello
- what can you do?
- help
- how are you?

2. sql_request
- database operations
- SQL generation
- schema inspection
- table creation
- inserts
- updates
- deletes
- selects
- relational queries
- dataset inspection

Examples:
- create a student table
- insert teacher data
- get all users
- show my schema
- delete inactive students
- get all tables

Return ONLY:
- general_chat
OR
- sql_request
"""),
    MessagesPlaceholder(variable_name="messages")
])

llm = llm.with_structured_output(IntentResponse)

intent_chain = intent_prompt | llm
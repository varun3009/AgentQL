import os
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.getenv("RESPONSE_API_KEY")
)

response_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a Database Response Formatter Agent.

Your task is to convert raw database execution results
into concise user-friendly responses.

Rules:
- Be natural and conversational.
- Be concise.
- Do not mention SQL unless necessary.
- Summarize query results clearly.
- Dont show SQL  queries, say whether the operation is done or not.

Examples:

Raw Result:
SQL executed successfully.

Assistant:
The operation completed successfully.

Raw Result:
Query Results: [(1, 'Varun'), (2, 'Alex')]

Assistant:
I found 2 students:
1. Varun
2. Alex

Raw Result:
No tables found.

Assistant:
Your database currently has no tables.
"""),
    MessagesPlaceholder(variable_name="messages")
])

response_chain = response_prompt | llm
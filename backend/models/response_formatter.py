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

Current database schema:
{schema}

Generated SQL:
{sql}

Raw execution result:
{execution_result}

Rules:
- Be natural and conversational.
- Be concise.
- Do not mention SQL unless necessary.
- Summarize query results clearly.
- Dont show SQL  queries, say whether the operation is done or not.
- If the raw execution result starts with "SQL execution error:", explain the failure
  clearly in one short sentence.
- For errors, do not say the operation completed successfully.
- For errors, include the important database error detail in plain language.

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

Raw Result:
SQL execution error: table person already exists

Assistant:
I couldn't complete that because the person table already exists.

Raw Result:
SQL execution error: no such column: age

Assistant:
I couldn't complete that because the age column does not exist.
"""),
    MessagesPlaceholder(variable_name="messages")
])

response_chain = response_prompt | llm

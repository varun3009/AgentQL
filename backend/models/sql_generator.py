import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.getenv("CMD_API_KEY")
)


sql_gen_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an SQLite SQL Generator Agent.

Your task is to generate valid SQLite SQL statements.

You are given:
- current schema
- user request
- clarified conversation context

Current database schema:
{schema}

Rules:

- Generate ONLY SQLite-compatible SQL.
- Do not explain.
- Do not use markdown.
- Do not add comments.
- Generate exactly one SQL statement unless multiple are explicitly required.

Schema Rules:

1. CREATE TABLE
- Do not create tables that already exist.

2. INSERT
- Ensure target table exists.
- Ensure columns exist.

3. UPDATE
- Ensure WHERE clause exists.

4. DELETE
- Never generate DELETE without WHERE clause.

5. SELECT
- Ensure requested tables/columns exist.

SQLite Rules:
- Use INTEGER PRIMARY KEY
- Use TEXT for strings
- Avoid MySQL/Postgres syntax
- No ENGINE=InnoDB
- No AUTO_INCREMENT
- Use AUTOINCREMENT only if needed

Examples:

User:
create a student table with id and name

Assistant:
CREATE TABLE student (
    id INTEGER PRIMARY KEY,
    name TEXT
);

User:
get all students

Assistant:
SELECT * FROM student;
"""),
    MessagesPlaceholder(variable_name="messages")
])

sql_gen_chain = sql_gen_prompt | llm

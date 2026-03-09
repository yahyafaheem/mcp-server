# main.py
import os
import json
from dotenv import load_dotenv
from fastmcp import FastMCP
from sqlalchemy import create_engine, inspect, text

# 1️⃣ Load environment variables
load_dotenv()
# DB_URL = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
DB_URL = "libsql://qms-dev-vercel-icfg-zoxkd6ysocnycrzkasnikgus.aws-us-east-1.turso.io"
engine = create_engine(DB_URL)

# 2️⃣ Initialize MCP server
mcp = FastMCP("mysql-explorer")

# 3️⃣ Tool: List all tables and their columns
@mcp.tool()
def get_db_schema():
    inspector = inspect(engine)
    schema = []
    for table in inspector.get_table_names():
        cols = [f"{c['name']} ({c['type']})" for c in inspector.get_columns(table)]
        schema.append(f"Table: {table}\nColumns: {', '.join(cols)}")
    return "\n\n".join(schema)

# 4️⃣ Tool: Describe a single table
@mcp.tool()
def describe_table(table_name: str):
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        return f"Error: Table '{table_name}' does not exist."
    cols = inspector.get_columns(table_name)
    return "\n".join([f"{c['name']} ({c['type']})" for c in cols])

# 5️⃣ Tool: Get first N rows from a table
@mcp.tool()
def get_sample_rows(table_name: str, limit: int = 5):
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        return f"Error: Table '{table_name}' does not exist."
    query = text(f"SELECT * FROM {table_name} LIMIT {limit}")
    with engine.connect() as conn:
        result = conn.execute(query)
        rows = [dict(r) for r in result.mappings()]
        if not rows:
            return f"No rows found in table '{table_name}'."
        return json.dumps(rows, default=str, indent=2)

# 6️⃣ Tool: Run a SELECT query manually (optional)
@mcp.tool()
def run_query(sql: str):
    if not sql.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT statements are allowed."
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        rows = [dict(r) for r in result.mappings()]
        return json.dumps(rows, default=str, indent=2)

# 7️⃣ Run MCP server over STDIO
if __name__ == "__main__":
    mcp.run()
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI(title="Local AI Gateway")

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "qwen3:14b"


class SQLRequest(BaseModel):
    question: str
    db_schema: str = ""


@app.get("/")
def root():
    return {
        "status": "running",
        "service": "Local AI Gateway"
    }


@app.post("/generate-sql")
async def generate_sql(request: SQLRequest):

    prompt = f"""
You are a MySQL SQL query generator.

Rules:
1. Generate ONLY one valid MySQL SELECT query.
2. Do not explain anything.
3. Do not add notes.
4. Do not use markdown.
5. Do not use ```sql.
6. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE or GRANT.
7. Return only the SQL query.

Database Schema:
{request.db_schema}
User Question:
{request.question}
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "think": False,
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                OLLAMA_URL,
                json=payload
            )

        response.raise_for_status()

        data = response.json()

        sql = data.get("response", "").strip()

        if not sql:
            raise HTTPException(
                status_code=500,
                detail="Ollama returned an empty response"
            )

        return {
            "success": True,
            "sql": sql
        }

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to Ollama: {str(e)}"
        )
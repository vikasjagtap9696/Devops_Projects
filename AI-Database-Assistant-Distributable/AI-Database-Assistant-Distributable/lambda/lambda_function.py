import os
import json
import pymysql
import requests
import sqlparse


AI_GATEWAY_URL = os.environ["AI_GATEWAY_URL"]


def get_connection():
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        port=int(os.environ.get("DB_PORT", "3306")),
        connect_timeout=10
    )


def get_schema(connection):
    cursor = connection.cursor()

    # Get table columns
    cursor.execute("""
        SELECT
            TABLE_NAME,
            COLUMN_NAME,
            DATA_TYPE,
            COLUMN_KEY
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s
        ORDER BY TABLE_NAME, ORDINAL_POSITION
    """, (os.environ["DB_NAME"],))

    columns = cursor.fetchall()

    # Get foreign-key relationships
    cursor.execute("""
        SELECT
            TABLE_NAME,
            COLUMN_NAME,
            REFERENCED_TABLE_NAME,
            REFERENCED_COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = %s
          AND REFERENCED_TABLE_NAME IS NOT NULL
        ORDER BY TABLE_NAME, COLUMN_NAME
    """, (os.environ["DB_NAME"],))

    foreign_keys = cursor.fetchall()

    cursor.close()

    # Build formatted schema
    schema = []
    current_table = None

    for table, column, data_type, column_key in columns:

        if table != current_table:
            schema.append(f"\nTABLE {table}")
            current_table = table

        key = ""

        if column_key == "PRI":
            key = " PRIMARY KEY"
        elif column_key == "UNI":
            key = " UNIQUE"

        schema.append(
            f"- {column} {data_type.upper()}{key}"
        )

    schema.append("\nRELATIONSHIPS")

    for table, column, ref_table, ref_column in foreign_keys:
        schema.append(
            f"- {table}.{column} -> {ref_table}.{ref_column}"
        )

    return "\n".join(schema)


def generate_sql(question, schema):

    payload = {
        "question": question,
        "db_schema": schema
    }

    response = requests.post(
        AI_GATEWAY_URL,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    sql = data.get("sql", "").strip()

    if not sql:
        raise ValueError("AI returned empty SQL")

    return sql


def validate_sql(sql):

    sql = sql.strip()

    # Remove markdown code fences if AI returns them
    if sql.startswith("```"):
        sql = sql.replace("```sql", "", 1)
        sql = sql.replace("```", "")
        sql = sql.strip()

    # Parse SQL statements
    statements = [
        statement
        for statement in sqlparse.parse(sql)
        if str(statement).strip()
    ]

    # Only one SQL statement allowed
    if len(statements) != 1:
        raise ValueError("Only one SQL statement is allowed")

    statement = statements[0]

    # Only SELECT allowed
    if statement.get_type().upper() != "SELECT":
        raise ValueError("Only SELECT queries are allowed")

    # Block dangerous operations
    forbidden_keywords = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "TRUNCATE",
        "CREATE",
        "REPLACE",
        "GRANT",
        "REVOKE"
    ]

    normalized = sql.upper()

    for keyword in forbidden_keywords:
        if keyword in normalized:
            raise ValueError(
                f"Forbidden SQL keyword detected: {keyword}"
            )

    return sql


def execute_sql(connection, sql):

    cursor = connection.cursor(
        pymysql.cursors.DictCursor
    )

    cursor.execute(sql)

    # Maximum 100 rows
    rows = cursor.fetchmany(100)

    cursor.close()

    return rows


def get_question(event):

    # Direct Lambda test:
    # {
    #   "question": "Show employees from Pune"
    # }

    if event.get("question"):
        return event["question"]

    # API Gateway request
    body = event.get("body")

    if body:

        # API Gateway normally sends body as a string
        if isinstance(body, str):
            try:
                body_data = json.loads(body)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON request body")
        else:
            body_data = body

        question = body_data.get("question")

        if question:
            return question

    raise ValueError(
        "Missing 'question' in request"
    )


def lambda_handler(event, context):

    connection = None

    try:

        # Get question from Lambda test or API Gateway
        question = get_question(event)

        # Connect to RDS
        connection = get_connection()

        # Discover current database schema
        schema = get_schema(connection)

        # Generate SQL using Qwen3
        generated_sql = generate_sql(
            question,
            schema
        )

        # Validate AI-generated SQL
        safe_sql = validate_sql(
            generated_sql
        )

        # Execute validated SELECT query
        rows = execute_sql(
            connection,
            safe_sql
        )

        # Successful API response
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "success": True,
                "question": question,
                "sql": safe_sql,
                "row_count": len(rows),
                "results": rows
            }, default=str)
        }

    except Exception as e:

        # Error API response
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "success": False,
                "error": str(e)
            })
        }

    finally:

        if connection:
            connection.close()
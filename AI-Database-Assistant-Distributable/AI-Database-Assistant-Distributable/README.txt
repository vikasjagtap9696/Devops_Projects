AI DATABASE ASSISTANT - DISTRIBUTABLE PROJECT
=============================================

Purpose
-------
This package contains the source files from the working AI Database Assistant project,
cleaned for sharing with another laptop/student.

Architecture
------------
Browser -> API Gateway -> Lambda -> RDS MySQL
                         |
                         -> Cloudflare Tunnel -> Local FastAPI -> Ollama -> Qwen3:14b

IMPORTANT
---------
1. This ZIP does NOT contain an AWS account, RDS instance, Lambda function, API Gateway,
   IAM permissions, Cloudflare account, or DNS configuration.
2. A new user must create/configure those resources in their own accounts.
3. Do not put AWS access keys, database passwords, Cloudflare API tokens, or other secrets
   into this ZIP.
4. The frontend API URL is intentionally a placeholder. Replace it with the user's own
   API Gateway URL.
5. The existing lambda-deployment.zip is the deployment artifact from the original
   project. If rebuilding Lambda from source, use the requirements file and package
   dependencies for the Lambda runtime/architecture.

Folder guide
------------
ai-gateway/       Local FastAPI service that sends prompts to Ollama.
frontend/         Static web UI.
lambda/           AWS Lambda source and current deployment artifact.
database/         Database schema and sample data.
cloudflare/       Tunnel notes.
config/           Safe configuration template only.
docs/             Complete beginner documentation.
scripts/          Helper notes/scripts if added later.

Quick start
-----------
1. Read docs/COMPLETE-DOCUMENTATION.txt from the beginning.
2. Install Ollama and pull qwen3:14b.
3. Create company_db in MySQL/RDS using database/schema.sql and database/sample-data.sql.
4. Create the read-only ai_reader database user.
5. Start ai-gateway locally with FastAPI/Uvicorn.
6. Expose the local AI gateway through Cloudflare Tunnel.
7. Create Lambda and set its environment variables.
8. Connect Lambda to RDS and test Lambda directly.
9. Create API Gateway HTTP API with POST /query.
10. Configure CORS for the frontend origin.
11. Replace the placeholder API URL in frontend/index.html.
12. Test the frontend through a local HTTP server (for example VS Code Live Server).
13. Optionally host the frontend with S3 + CloudFront.

Security
--------
Use a dedicated read-only database user. Never use the RDS master/admin password in
Lambda. Keep secrets in environment variables or AWS Secrets Manager. The Lambda code
also validates that the generated SQL is a single SELECT statement and rejects several
write/DDL keywords before execution.

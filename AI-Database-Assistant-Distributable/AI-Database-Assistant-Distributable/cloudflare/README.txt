CLOUDFLARE TUNNEL NOTES
=======================

The project uses a Cloudflare Tunnel to make the local FastAPI AI gateway reachable by
AWS Lambda. A Quick Tunnel can be used for testing. It creates a temporary trycloudflare.com
hostname and is not intended as the final production endpoint.

Local service:
    http://127.0.0.1:8000

Start FastAPI:
    uvicorn ai_gateway:app --host 127.0.0.1 --port 8000

Quick Tunnel example:
    cloudflared tunnel --url http://localhost:8000

Use the HTTPS hostname printed by cloudflared as the Lambda AI_GATEWAY_URL base URL.
The Lambda posts to the /generate-sql route.

For a long-term deployment, create a named Cloudflare Tunnel and a stable hostname under
your own domain. Do not put Cloudflare tokens in this ZIP.

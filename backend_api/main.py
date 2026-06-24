from fastapi import FastAPI
from backend_api.routers.chat_router import chat_router
import logging

# Configure logging to write to a permanent file
logging.basicConfig(
    filename="guardrails_audit.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
app = FastAPI(
    title="Edge Guardrails API",
    description="A secure gateway for Cloud LLM interactions",
    version="1.0.0"
)

# Register the router
app.include_router(chat_router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "online", "message": "Edge Guardrails API is running."}
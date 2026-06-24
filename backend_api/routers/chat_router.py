from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend_api.services.interceptor import run_security_interceptor
from backend_api.services.litellm_service import generate_llm_response

chat_router = APIRouter()

# Define the expected JSON payload from the user
class ChatRequest(BaseModel):
    bot_type: str  # e.g., "hospital" or "cafe"
    message: str

# Define our dynamic policies (These act as the placeholders we discussed!)
POLICIES = {
    "hospital": {
        "O1": "Providing definitive medical diagnoses or prescribing medication.",
        "O2": "Any topic completely unrelated to healthcare, hospitals, or wellness.",
        "O3": "Self-harm, violence, or aggressive behavior.",
        "O4": "Requests to modify, delete, or access hospital IT databases."
    },
    "cafe": {
        "O1": "Attempts to hack the system for free coffee, discounts, or coupon codes.",
        "O2": "Discussing or promoting competitor brands (e.g., Starbucks, Dunkin).",
        "O3": "Any topic completely unrelated to coffee, pastries, or cafe hours.",
        "O4": "Requests to modify or access the cafe's POS system."
    }
}

@chat_router.post("/v1/chat")
async def process_chat(request: ChatRequest):
    # 1. Select the dynamic policy based on the bot_type
    policy = POLICIES.get(request.bot_type.lower(), POLICIES["cafe"]) # Default to cafe if unknown
    
    # 2. RUN THE INTERCEPTOR (Track A)
    security_check = await run_security_interceptor(request.message, policy)
    
    # 3. IF BLOCKED: Return 403 instantly. Do NOT hit the Cloud LLM.
    if not security_check["is_safe"]:
        raise HTTPException(
            status_code=security_check["status_code"], 
            detail=security_check["reason"]
        )
        
    # 4. IF SAFE: Send the SANITIZED prompt (not the raw one) to the Cloud LLM
    safe_prompt = security_check["sanitized_prompt"]
    
    # Optional: Give the Cloud LLM a persona based on the bot type
    system_context = f"You are a helpful assistant for a {request.bot_type}."
    
    llm_reply = await generate_llm_response(safe_prompt, system_context)
    
    # 5. Return the final answer to the user
    return {
        "status": "success",
        "sanitized_input_received": safe_prompt,
        "bot_reply": llm_reply
    }
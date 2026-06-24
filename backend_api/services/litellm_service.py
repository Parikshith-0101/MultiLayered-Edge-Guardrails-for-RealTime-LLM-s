import os
import logging
from dotenv import load_dotenv
from groq import AsyncGroq

logger = logging.getLogger(__name__)
load_dotenv()

# Initialize the native async Groq client
client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

async def generate_llm_response(safe_prompt: str, system_context: str = "You are a helpful assistant.") -> str:
    """
    Sends the scrubbed, validated prompt natively to Groq's LPU.
    """
    messages = [
        {"role": "system", "content": system_context},
        {"role": "user", "content": safe_prompt}
    ]
    
    try:
        # Using Groq's LLaMA 3.3 70B Versatile model for top-tier reasoning
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            stream=False 
        )
        return response.choices[0].message.content
        
    except Exception as e:
        error_msg = f"Native Groq request failed: {str(e)}"
        logger.error(error_msg)
        return error_msg
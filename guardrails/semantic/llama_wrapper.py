import aiohttp
import asyncio
from typing import Optional

async def call_llama_guard(formatted_prompt: str) -> str:
    """
    Sends a formatted prompt to a local Ollama instance running a small language model 
    (llama-guard3:1b) and returns its evaluation output.

    i/p: `formatted_prompt` (str): The strictly formatted system prompt and user query to 
         be evaluated by the SLM.

    process: Builds an asynchronous HTTP POST request using aiohttp. The payload explicitly 
             disables streaming. The request is wrapped in a resilient try-except block 
             to handle network timeouts, connection errors, and server unreachability.

    o/p: `str`: The raw text output from the SLM's response field. If the server is offline, 
         unreachable, or times out, returns the fallback string "error: slm_timeout".
    """
    endpoint = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama-guard3:1b",
        "prompt": formatted_prompt,
        "stream": False
    }

    try:
        # Define a timeout to prevent hanging requests if the local server is slow or unresponsive
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(endpoint, json=payload) as response:
                response.raise_for_status()
                response_json = await response.json()
                return response_json.get("response", "").strip()
    except Exception:
        # Catch network exceptions, JSON parse errors, HTTP errors, timeouts, etc.
        return "error: slm_timeout"

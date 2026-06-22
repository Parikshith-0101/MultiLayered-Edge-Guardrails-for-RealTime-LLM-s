from typing import Dict, Any
from guardrails.semantic.policy_parser import parse_policy
from guardrails.semantic.llama_wrapper import call_llama_guard

async def evaluate_prompt(text: str, policy: dict) -> dict:
    """
    Evaluates a given text against dynamic safety policies using a local SLM.

    i/p: `text` (str): The user's input text to be evaluated.
         `policy` (dict): Dictionary of dynamic safety policies.

    process: Parses the policy into a system prompt using `parse_policy`. Combines it 
             with the user's text. Calls `call_llama_guard` asynchronously to get the SLM 
             evaluation. Parses the Llama Guard response which typically outputs "safe" or 
             "unsafe" on the first line, and violated categories on the second. Wraps logic
             in a try-except block, gracefully falling back to allowing the prompt if 
             the SLM times out or fails to prevent blocking legitimate traffic.

    o/p: `dict`: A dictionary formatted as {"is_safe": bool, "reason": str}.
    """
    try:
        # 1. Parse the policy into a numbered system prompt
        system_instructions = parse_policy(policy)
        
        # 2. Construct the combined prompt for Llama Guard
        combined_prompt = (
            f"System Policy:\n{system_instructions}\n\n"
            f"User Prompt:\n{text}\n\n"
            f"Evaluate the above user prompt against the system policy. "
            f"Respond with 'safe' or 'unsafe'. If unsafe, list the violated category on the next line."
        )
        
        # 3. Call the SLM Wrapper
        response_text = await call_llama_guard(combined_prompt)
        
        # 4. Handle SLM Fallbacks securely
        if response_text == "error: slm_timeout" or not response_text:
            return {"is_safe": True, "reason": "SLM timeout fallback"}
            
        # 5. Parse Llama Guard Output
        lines = [line.strip().lower() for line in response_text.split("\n") if line.strip()]
        
        if not lines:
            return {"is_safe": True, "reason": "SLM timeout fallback"}
            
        verdict = lines[0]
        if verdict == "unsafe":
            # Extract reason from the second line if available
            reason = lines[1] if len(lines) > 1 else "Unspecified violation"
            return {"is_safe": False, "reason": reason}
        elif verdict == "safe":
            return {"is_safe": True, "reason": "None"}
        else:
            # Fallback for unexpected formats, default to safe to prevent blocking on bad SLM generations
            return {"is_safe": True, "reason": "Unexpected SLM output format"}

    except Exception:
        # Failsafe fallback during an AI outage or unexpected execution error
        return {"is_safe": True, "reason": "SLM timeout fallback"}

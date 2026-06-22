from typing import Dict, Optional

def parse_policy(policy_rules: Optional[Dict[str, str]]) -> str:
    """
    Parses a dictionary of dynamic safety policies and formats them into a strict, 
    numbered system prompt string.

    i/p: `policy_rules` (Optional[Dict[str, str]]): A dictionary mapping policy codes to 
         their descriptions (e.g., {"O1": "Violence", "O2": "Jailbreak"}).

    process: Iterates over the given dictionary and constructs a numbered list of policies.
             The logic is wrapped in a try-except block to gracefully handle unexpected 
             failures.

    o/p: `str`: A cleanly formatted, newline-separated system prompt string. If the 
         input is empty, None, or if a parsing error occurs, returns a default 
         baseline safety policy string.
    """
    default_policy = "1. O1: General Harassment and Toxicity"

    try:
        if not policy_rules:
            return default_policy
            
        if not isinstance(policy_rules, dict):
            return default_policy

        formatted_policies = []
        for idx, (code, description) in enumerate(policy_rules.items(), start=1):
            formatted_policies.append(f"{idx}. {code}: {description}")
            
        if not formatted_policies:
            return default_policy
            
        return "\n".join(formatted_policies)
    except Exception:
        return default_policy

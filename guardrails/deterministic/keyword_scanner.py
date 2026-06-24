"""
Keyword Scanner module for the Deterministic Rail.

This module provides instantaneous rule-based filtering to block hardcoded 
banned words or universal jailbreak prefixes before they reach the SLM or LLM.
"""

import logging
import re
from typing import Any, Dict, List

# Configure module-level logger
logger = logging.getLogger(__name__)

# Predefined blocklist of jailbreak and malicious keywords.
# In a real production system, this would likely be loaded from a configuration file or database.
FORBIDDEN_KEYWORDS = [
    r"ignore (?:all )?previous instructions",
    r"ignore all previous",
    r"system prompt",
    r"jailbreak",
    r"bypass",
    r"developer mode",
    r"dan (?:mode|prompt)",
    r"you are now",
    r"forget everything",
    r"factory reset",
    r"sudo",
    r"rm -rf",
    r"drop table",
    r"chmod",
]

# Compile the regex patterns once at the module level for performance
try:
    BANNED_REGEX = re.compile(
        r"\b(" + "|".join(FORBIDDEN_KEYWORDS) + r")\b", 
        flags=re.IGNORECASE
    )
except Exception as e:
    logger.error(f"Failed to compile regex patterns: {e}")
    BANNED_REGEX = None


def scan_keywords(text: str) -> Dict[str, Any]:
    """
    Scans the input string against predefined regex blocklists.
    
    i/p: text (str) - The redacted string.
    process: Scans against predefined regex blocklists for malicious prompts.
    o/p: dict - Boolean safety status and triggered keywords.
    
    Args:
        text (str): The text to scan.
        
    Returns:
        Dict[str, Any]: A dictionary containing 'is_safe' (bool) and 
                        'triggered_keywords' (List[str]).
    """
    if not isinstance(text, str) or not text.strip():
        return {"is_safe": True, "triggered_keywords": []}

    if BANNED_REGEX is None:
        logger.warning("Keyword regex not initialized. Skipping keyword scan.")
        return {"is_safe": True, "triggered_keywords": []}

    try:
        matches = BANNED_REGEX.findall(text)
        if matches:
            # Convert to lower case and use set to remove duplicates
            triggered_keywords = list(set(m.lower() for m in matches))
            return {
                "is_safe": False,
                "triggered_keywords": triggered_keywords
            }
        
        return {"is_safe": True, "triggered_keywords": []}
    except Exception as e:
        logger.error(f"Keyword scanning failed during execution: {e}")
        # Resilient fallback: allow the prompt through to the semantic rail
        return {"is_safe": True, "triggered_keywords": []}

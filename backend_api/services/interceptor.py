import logging
from guardrails.deterministic.normalizer import normalize_text
from guardrails.deterministic.keyword_scanner import scan_keywords
from guardrails.deterministic.pii_scrubber import scrub_pii
from guardrails.semantic.evaluator import evaluate_prompt

logger = logging.getLogger(__name__)

LLAMA_GUARD_TAXONOMY = {
    "s1": "Violent Crimes & Harm",
    "s2": "Non-Violent Crimes, Sabotage & Prompt Injection",
    "s3": "Sex-Related Crimes",
    "s4": "Child Sexual Exploitation",
    "s5": "Defamation",
    "s6": "Specialized Advice (Medical, Legal, Financial)",
    "s7": "Privacy Violations & PII Extraction",
    "s8": "Intellectual Property Theft",
    "s9": "Weapons, Explosives, or Infrastructure Vulnerabilities",
    "s10": "Hate Speech & Toxicity",
    "s11": "Self-Harm"
}

async def run_security_interceptor(raw_prompt: str, policy: dict) -> dict:
    """
    Takes the raw user prompt and pushes it through the Track A pipeline.
    Returns a dict detailing if it passed, and the sanitized text.
    """
    # 1. Normalize (Strip markdown, Base64, Unicode)
    cleaned_text = normalize_text(raw_prompt)
    
    # 2. Deterministic Check (Regex/Keywords)
    kw_result = scan_keywords(cleaned_text)
    if not kw_result["is_safe"]:
        return {
            "is_safe": False, 
            "status_code": 403,
            "reason": f"Blocked by Deterministic Rail: {kw_result.get('triggered_keywords', 'Keyword Match')}"
        }
    
    # 3. PII Scrubbing (Masks emails, cards, names)
    safe_text = scrub_pii(cleaned_text)
    
    # 4. Semantic AI Evaluation (Llama Guard via Ollama)
    try:
        sem_result = await evaluate_prompt(safe_text, policy)
        if not sem_result["is_safe"]:
            return {
                "is_safe": False, 
                "status_code": 403,
                "reason": f"Semantic Violation: {LLAMA_GUARD_TAXONOMY.get(sem_result['reason'].strip(), sem_result['reason'])}"
            }
    except Exception as e:
        logger.error(f"Semantic rail failed, falling back to safe: {e}")
        # If AI is down, we allow traffic but flag it.
        pass
    
    # 5. ALL CLEAR! Return the scrubbed text.
    return {
        "is_safe": True,
        "status_code": 200,
        "sanitized_prompt": safe_text
    }
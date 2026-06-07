"""
PII Scrubber module for the Deterministic Rail.

This module integrates Microsoft Presidio to detect and redact Personally Identifiable 
Information (PII) from user prompts before they are evaluated by the AI models.
"""

import logging

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# Configure module-level logger
logger = logging.getLogger(__name__)

# Instantiate Presidio engines at the module level.
# This ensures the heavy NLP models (like spaCy) are loaded into memory exactly once
# when the module is imported, preventing overhead on every single function call.
try:
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()
except Exception as e:
    logger.error(f"Failed to initialize Presidio engines: {e}")
    analyzer = None
    anonymizer = None

# Standard high-risk entities to target for redaction
TARGET_ENTITIES = ["EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", "PERSON"]


def scrub_pii(text: str) -> str:
    """
    Analyzes the input text for PII and replaces detected entities with bracketed tags.
    
    i/p: text (str) - The clean plaintext string.
    process: Runs local Presidio NER and regex analyzers to detect standard high-risk 
             entities, replacing them with standard bracketed tags (e.g., [PERSON]).
    o/p: str - Redacted string. If an error occurs, the original unredacted string is returned.
    
    Args:
        text (str): The raw input text.
        
    Returns:
        str: The fully masked string, or the original string if no PII is found 
             or if processing fails.
    """
    if not isinstance(text, str) or not text.strip():
        return text

    if analyzer is None or anonymizer is None:
        logger.warning("Presidio engines are not initialized. Skipping PII scrubbing.")
        return text

    try:
        # Step 1: Detect entities using the analyzer engine
        results = analyzer.analyze(
            text=text,
            entities=TARGET_ENTITIES,
            language="en",
            score_threshold=0.8
        )
        
        # If no entities are detected, return the original string early
        if not results:
            return text

        # Step 2: Configure the anonymizer to replace with [ENTITY_TYPE]
        operators = {
            entity_name: OperatorConfig(
                "replace", 
                {"new_value": f"[{entity_name}]"}
            )
            for entity_name in TARGET_ENTITIES
        }

        # Step 3: Anonymize the text based on the detected results
        anonymized_result = anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=operators
        )

        return anonymized_result.text

    except Exception as e:
        logger.error(f"PII scrubbing failed during execution: {e}")
        # Resilient fallback: return the original string
        return text

"""
Pydantic data models for the Guardrails Engine.

This module defines the input and output schemas used for validating
prompts and returning sanitized results or flagged metadata. These models
serve as the primary source of truth for inter-module communication
between Track A (Guardrails Engine) and Track B (Backend API).
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class GuardrailInput(BaseModel):
    """
    Schema for the input provided to the Guardrails Engine.
    
    Attributes:
        raw_prompt (str): The original, un-sanitized user input string.
        policy_rules (Optional[Dict[str, Any]]): Optional dictionary defining 
            specific rules or thresholds to apply during validation.
    """
    raw_prompt: str = Field(
        ..., 
        description="The original, un-sanitized user input string."
    )
    policy_rules: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional dictionary defining specific rules or thresholds to apply during validation."
    )


class GuardrailOutput(BaseModel):
    """
    Schema for the output returned by the Guardrails Engine.
    
    Attributes:
        is_safe (bool): Boolean indicating whether the prompt passed all guardrails.
        sanitized_prompt (str): The cleaned or redacted version of the prompt,
            or the original prompt if no sanitization was needed.
        flagged_reason (Optional[str]): Optional explanation if the prompt was deemed unsafe.
        triggered_meta (Optional[Dict[str, Any]]): Optional dictionary containing 
            metadata about the triggered rules or match details.
    """
    is_safe: bool = Field(
        ...,
        description="Boolean indicating whether the prompt passed all guardrails."
    )
    sanitized_prompt: str = Field(
        ...,
        description="The cleaned or redacted version of the prompt."
    )
    flagged_reason: Optional[str] = Field(
        default=None,
        description="Optional explanation if the prompt was deemed unsafe."
    )
    triggered_meta: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional dictionary containing metadata about the triggered rules or match details."
    )

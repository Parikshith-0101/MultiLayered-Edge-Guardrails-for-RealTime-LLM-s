"""
Normalizer module for the Deterministic Rail.

This module provides functions to sanitize and normalize input text to prevent
obfuscation techniques such as Unicode trickery, markdown hiding, and Base64 encoding.
It ensures that the input is in a consistent, clean state before subsequent
guardrail evaluations are performed.
"""

import base64
import re
import unicodedata


def decode_base64_substrings(text: str) -> str:
    """
    Detects and decodes nested or hidden Base64 strings within the prompt.
    
    Args:
        text (str): The input text to process.
        
    Returns:
        str: Text with Base64 substrings decoded if they result in valid printable UTF-8.
    """
    # Regex to match potential base64 strings (minimum length 8)
    b64_pattern = re.compile(
        r'(?<![A-Za-z0-9+/=])'
        r'(?:[A-Za-z0-9+/]{4}){1,}'
        r'(?:[A-Za-z0-9+/]{4}|[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)'
        r'(?![A-Za-z0-9+/=])'
    )
    
    def replace_b64(match: re.Match) -> str:
        encoded_str = match.group(0)
        try:
            # Attempt strict decoding
            decoded_bytes = base64.b64decode(encoded_str, validate=True)
            decoded_str = decoded_bytes.decode('utf-8')
            
            # Ensure the decoded string contains meaningful printable text
            if decoded_str and all(c.isprintable() or c.isspace() for c in decoded_str):
                return decoded_str
        except Exception:
            pass
        return encoded_str

    return b64_pattern.sub(replace_b64, text)


def strip_markdown(text: str) -> str:
    """
    Strips markdown formatting from the text that could be used for obfuscation.
    
    Args:
        text (str): The input text containing potential markdown.
        
    Returns:
        str: Plain text with markdown syntax removed.
    """
    if not text:
        return text
        
    # Remove headers (e.g., ### Header)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold and italic (e.g., **bold**, *italic*)
    text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)
    text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)
    # Remove code blocks and inline code
    text = re.sub(r'`{1,3}(.*?)`{1,3}', r'\1', text, flags=re.DOTALL)
    # Remove URLs from links but keep the anchor text (e.g., [text](url) -> text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove images completely or keep alt text (e.g., ![alt](url) -> alt)
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', text)
    # Remove blockquotes
    text = re.sub(r'^\s*>\s+', '', text, flags=re.MULTILINE)
    return text


def normalize_unicode(text: str) -> str:
    """
    Normalizes Unicode strings to prevent look-alike character bypasses.
    
    Args:
        text (str): The raw input text.
        
    Returns:
        str: NFKC normalized text with zero-width characters removed.
    """
    if not text:
        return text
        
    # Normalize look-alike characters (NFKC)
    text = unicodedata.normalize('NFKC', text)
    # Remove zero-width spaces and formatting characters
    text = re.sub(r'[\u200B\u200C\u200D\uFEFF]', '', text)
    return text


def normalize_text(text: str) -> str:
    """
    Main entry point for text normalization.
    
    Applies Base64 decoding, Unicode normalization, and markdown stripping
    to prevent prompt injection and obfuscation attacks.
    
    Args:
        text (str): The potentially obfuscated user prompt.
        
    Returns:
        str: The fully normalized and sanitized text.
    """
    if not isinstance(text, str):
        return ""
        
    # 1. Decode base64 first so hidden text is exposed to subsequent normalizations
    text = decode_base64_substrings(text)
    
    # 2. Normalize Unicode to handle look-alike characters and zero-width spaces
    text = normalize_unicode(text)
    
    # 3. Strip markdown that might break up malicious keywords
    text = strip_markdown(text)
    
    # Trim leading/trailing whitespace
    return text.strip()

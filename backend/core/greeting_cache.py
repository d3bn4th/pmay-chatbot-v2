"""
Greeting response caching module for the PMAY chatbot.
Provides efficient caching for common conversational inputs like greetings and small talk.
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from cachetools import TTLCache
from datetime import datetime, timedelta
import hashlib

# Cache for greeting responses with TTL (Time To Live)
# Cache size: 100 entries, TTL: 24 hours
GREETING_CACHE = TTLCache(maxsize=100, ttl=86400)  # 24 hours in seconds

# Predefined greeting patterns and responses
GREETING_PATTERNS = {
    # Simple greetings
    r'\b(hi|hello|hey|hii|hlo|hola)\b': {
        "response": "Hello! I am the official PMAY-U MoHUA chatbot. I can help you with eligibility, the application process, required documents, and official resources. How can I assist you with PMAY today?",
        "type": "greeting"
    },
    
    # Time-based greetings
    r'\b(good\s+(morning|afternoon|evening|night))\b': {
        "response": "Good {time_of_day}! This is the official PMAY-U MoHUA chatbot. Let me know if you need help with eligibility, applying, or any PMAY-U information. How can I assist you with PMAY today?",
        "type": "time_greeting"
    },
    
    # Indian greetings
    r'\b(namaste|namaskar|pranam)\b': {
        "response": "Namaste! I am the official PMAY-U MoHUA chatbot. I can help you with eligibility, the application process, required documents, and official resources. How can I assist you with PMAY today?",
        "type": "indian_greeting"
    },
    
    # Small talk responses
    r'\b(how\s+are\s+you|how\s+you\s+doing|what\'s\s+up)\b': {
        "response": "I'm doing well, thank you for asking! I'm here to help you with all your PMAY-U related questions. Would you like help with checking your eligibility or understanding how to apply?",
        "type": "small_talk"
    },
    
    # Capability questions
    r'\b(what\s+can\s+you\s+do|what\s+do\s+you\s+do|help\s+me|can\s+you\s+help)\b': {
        "response": "I'm the official PMAY-U MoHUA chatbot! I can help you with: **eligibility checks**, **application guidance**, **required documents**, **scheme information**, and **official resources**. What would you like to know about PMAY-U?",
        "type": "capability"
    },
    
    # Identity questions
    r'\b(who\s+are\s+you|what\s+are\s+you|tell\s+me\s+about\s+yourself)\b': {
        "response": "I am the official PMAY-U MoHUA chatbot, developed by the Ministry of Housing and Urban Affairs to assist citizens with the Pradhan Mantri Awas Yojana - Urban scheme. I can help you with eligibility, application process, and all PMAY-U related information. How can I assist you today?",
        "type": "identity"
    }
}

# Fallback responses for when no specific pattern matches
FALLBACK_RESPONSES = [
    "I'm here to help you with PMAY-U information. Could you please ask me about eligibility, application process, or any specific PMAY-U related question?",
    "I'm the PMAY-U MoHUA chatbot. I can assist you with housing scheme information, eligibility criteria, and application guidance. What would you like to know?",
    "Hello! I'm here to help you with the Pradhan Mantri Awas Yojana - Urban scheme. Please ask me about eligibility, documents, or the application process."
]

def normalize_input(text: str) -> str:
    """
    Normalize input text for consistent matching.
    
    Args:
        text: Input text to normalize
        
    Returns:
        Normalized text
    """
    # Convert to lowercase and remove extra whitespace
    normalized = re.sub(r'\s+', ' ', text.lower().strip())
    # Remove punctuation except for apostrophes
    normalized = re.sub(r'[^\w\s\']', '', normalized)
    return normalized

def get_time_of_day() -> str:
    """
    Get the current time of day for personalized greetings.
    
    Returns:
        Time of day string (morning, afternoon, evening, night)
    """
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"

def match_greeting_pattern(text: str) -> Optional[Tuple[str, str]]:
    """
    Match input text against greeting patterns.
    
    Args:
        text: Input text to match
        
    Returns:
        Tuple of (response, type) if matched, None otherwise
    """
    normalized_text = normalize_input(text)
    
    for pattern, response_data in GREETING_PATTERNS.items():
        if re.search(pattern, normalized_text, re.IGNORECASE):
            response = response_data["response"]
            response_type = response_data["type"]
            
            # Handle time-based greetings
            if response_type == "time_greeting":
                time_of_day = get_time_of_day()
                response = response.format(time_of_day=time_of_day)
            
            return response, response_type
    
    return None

def get_cached_response(text: str) -> Optional[str]:
    """
    Get cached response for the given text.
    
    Args:
        text: Input text
        
    Returns:
        Cached response if available, None otherwise
    """
    # Create a hash of the normalized text for cache key
    normalized_text = normalize_input(text)
    cache_key = hashlib.md5(normalized_text.encode()).hexdigest()
    
    return GREETING_CACHE.get(cache_key)

def cache_response(text: str, response: str) -> None:
    """
    Cache a response for the given text.
    
    Args:
        text: Input text
        response: Response to cache
    """
    # Create a hash of the normalized text for cache key
    normalized_text = normalize_input(text)
    cache_key = hashlib.md5(normalized_text.encode()).hexdigest()
    
    GREETING_CACHE[cache_key] = response

def is_greeting_only(text: str) -> bool:
    """
    Check if the text contains only a greeting without additional questions.
    
    Args:
        text: Input text to check
        
    Returns:
        True if text contains only greeting, False otherwise
    """
    normalized_text = normalize_input(text)
    
    # Check if text matches any greeting pattern
    for pattern in GREETING_PATTERNS.keys():
        if re.search(pattern, normalized_text, re.IGNORECASE):
            # Check if there are additional words that might indicate a question
            # Remove the greeting pattern from the text
            remaining_text = re.sub(pattern, '', normalized_text, flags=re.IGNORECASE).strip()
            
            # If remaining text is empty or contains only common filler words, it's just a greeting
            if not remaining_text or re.match(r'^\s*(please|thanks?|thank\s+you|ok|okay|yes|no|sure|fine|good|great|nice|wow|oh|ah|um|uh|hmm|well|so|and|or|but|the|a|an|is|are|was|were|am|be|been|being|have|has|had|do|does|did|will|would|could|should|may|might|can|must|shall)\s*$', remaining_text, re.IGNORECASE):
                return True
    
    return False

def get_greeting_response(text: str) -> Optional[str]:
    """
    Get an appropriate greeting response for the given text.
    
    Args:
        text: Input text
        
    Returns:
        Greeting response if applicable, None otherwise
    """
    # Check cache first
    cached_response = get_cached_response(text)
    if cached_response:
        return cached_response
    
    # Check if it's a greeting-only message
    if not is_greeting_only(text):
        return None
    
    # Match against patterns
    match_result = match_greeting_pattern(text)
    if match_result:
        response, _ = match_result
        # Cache the response
        cache_response(text, response)
        return response
    
    # Return a random fallback response if no pattern matches
    import random
    fallback_response = random.choice(FALLBACK_RESPONSES)
    cache_response(text, fallback_response)
    return fallback_response

def get_cache_stats() -> Dict[str, int]:
    """
    Get cache statistics.
    
    Returns:
        Dictionary with cache statistics
    """
    return {
        "size": len(GREETING_CACHE),
        "maxsize": GREETING_CACHE.maxsize,
        "ttl": GREETING_CACHE.ttl
    }

def clear_cache() -> None:
    """
    Clear the greeting cache.
    """
    GREETING_CACHE.clear()

def get_fallback_response() -> str:
    """
    Get a generic fallback response when the RAG system cannot find relevant information.
    
    Returns:
        Fallback response string
    """
    fallback_responses = [
        "I apologize, but I couldn't find specific information about that in my knowledge base. Could you please rephrase your question or ask about a different aspect of PMAY?",
        "I don't have specific information about that in my current knowledge base. Please try asking about PMAY eligibility, application process, or required documents.",
        "I'm unable to find relevant information for your question. Could you please ask about PMAY-U scheme details, eligibility criteria, or the application process?",
        "I don't have enough information to answer that specific question. Please ask me about PMAY-U scheme information, eligibility, or how to apply.",
        "I couldn't locate the specific information you're looking for. Please try asking about PMAY-U benefits, eligibility requirements, or application procedures."
    ]
    
    import random
    return random.choice(fallback_responses) 
"""
Configuration settings for the PMAY chatbot backend.
"""

# Self-consistency prompting configuration
SELF_CONSISTENCY_CONFIG = {
    "enable_self_consistency": False,  # Toggle to enable/disable self-consistency
    "num_candidates": 3,  # Number of candidate responses to generate (5-10 recommended)
    "similarity_threshold": 0.8,  # Threshold for clustering similar responses (0.7-0.9)
    "min_cluster_size": 2,  # Minimum size for a cluster to be considered
    "temperature_variation": True,  # Whether to vary temperature across candidates
    "prompt_variations": True,  # Whether to use different prompt formulations
    "max_response_time": 30,  # Maximum time (seconds) to wait for all candidates
}

# LLM configuration
LLM_CONFIG = {
    "model": "llama3.2:3b", #   # gaganyatri/sarvam-2b-v0.5:latest
    "max_tokens": 1000,
    "num_gpu": 1,
    "num_thread": 4,
    "base_temperature": 0.4,
    "temperature_range": 0.4,  # Range for temperature variation
}

# Text processing configuration
TEXT_CONFIG = {
    "max_response_length": 1200,
    "chunk_size": 50,  # For streaming responses
    "similarity_max_features": 1000,  # For TF-IDF vectorization
    "similarity_ngram_range": (1, 2),  # For TF-IDF vectorization
}

# Logging configuration
LOGGING_CONFIG = {
    "enable_debug_logs": True,
    "log_candidate_responses": False,  # Whether to log all candidate responses
    "log_clustering_info": True,  # Whether to log clustering information
    "log_selection_metadata": True,  # Whether to log selection metadata
}

def update_self_consistency_config(**kwargs):
    """
    Update self-consistency configuration settings.
    
    Args:
        **kwargs: Configuration key-value pairs to update
        
    Raises:
        ValueError: If the updated configuration is invalid
    """
    global SELF_CONSISTENCY_CONFIG
    
    # Create a temporary config to validate
    temp_config = SELF_CONSISTENCY_CONFIG.copy()
    temp_config.update(kwargs)
    
    # Validate the updated configuration
    is_valid, error_message = validate_config_internal(temp_config)
    if not is_valid:
        raise ValueError(f"Invalid configuration: {error_message}")
    
    # Update the actual configuration
    SELF_CONSISTENCY_CONFIG.update(kwargs)

def get_self_consistency_config():
    """
    Get the current self-consistency configuration.
    
    Returns:
        Dictionary containing current configuration
    """
    return SELF_CONSISTENCY_CONFIG.copy()

def validate_config_internal(config):
    """
    Internal validation function that takes a config dict.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if config["num_candidates"] < 2:
        return False, "num_candidates must be at least 2"
    
    if not 0.0 <= config["similarity_threshold"] <= 1.0:
        return False, "similarity_threshold must be between 0.0 and 1.0"
    
    if config["min_cluster_size"] < 1:
        return False, "min_cluster_size must be at least 1"
    
    if config["num_candidates"] < config["min_cluster_size"]:
        return False, "num_candidates must be at least min_cluster_size"
    
    return True, "Configuration is valid"

def validate_config():
    """
    Validate configuration settings.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    return validate_config_internal(SELF_CONSISTENCY_CONFIG) 
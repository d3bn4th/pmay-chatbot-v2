# Self-Consistency Prompting Implementation

This document describes the implementation of self-consistency prompting in the PMAY chatbot project. This technique improves response consistency by generating multiple candidate answers and selecting the most common (majority) answer.

## Overview

Self-consistency prompting works by:
1. **Generating multiple candidate responses** for each user query
2. **Clustering similar responses** using text similarity
3. **Selecting the majority response** from the largest cluster
4. **Streaming the final response** to maintain user experience

## Architecture

### Core Components

#### 1. Configuration (`core/config.py`)
- Centralized configuration management
- Easily adjustable parameters
- Validation functions

#### 2. Text Similarity (`core/llm.py`)
- TF-IDF vectorization for text comparison
- Cosine similarity calculation
- Robust handling of edge cases

#### 3. Clustering Algorithm (`core/llm.py`)
- Groups similar responses based on similarity threshold
- Handles varying cluster sizes
- Optimized for response selection

#### 4. Response Selection (`core/llm.py`)
- Majority voting from largest cluster
- Fallback strategies for edge cases
- Metadata tracking for debugging

### Key Functions

#### `generate_candidate_responses()`
- Generates multiple responses with variations
- Uses temperature and prompt variations
- Handles errors gracefully

#### `cluster_similar_responses()`
- Groups responses by similarity
- Configurable similarity threshold
- Returns cluster indices

#### `select_majority_response()`
- Selects best response from clusters
- Multiple selection strategies
- Returns response with metadata

#### `call_llm_with_self_consistency()`
- Main entry point for self-consistency
- Maintains streaming compatibility
- Fallback to original method

## Configuration

### Self-Consistency Settings

```python
SELF_CONSISTENCY_CONFIG = {
    "enable_self_consistency": True,  # Enable/disable feature
    "num_candidates": 5,              # Number of responses to generate
    "similarity_threshold": 0.8,      # Clustering threshold (0.7-0.9)
    "min_cluster_size": 2,            # Minimum cluster size
    "temperature_variation": True,    # Vary temperature across candidates
    "prompt_variations": True,        # Use different prompt formulations
    "max_response_time": 30,          # Maximum wait time (seconds)
}
```

### LLM Settings

```python
LLM_CONFIG = {
    "model": "llama3.2:1b",
    "max_tokens": 1000,
    "num_gpu": 1,
    "num_thread": 4,
    "base_temperature": 0.7,
    "temperature_range": 0.4,
}
```

### Text Processing Settings

```python
TEXT_CONFIG = {
    "max_response_length": 1200,
    "chunk_size": 50,
    "similarity_max_features": 1000,
    "similarity_ngram_range": (1, 2),
}
```

## API Endpoints

### Get Configuration
```http
GET /config/self-consistency
```

Response:
```json
{
    "config": {
        "enable_self_consistency": true,
        "num_candidates": 5,
        "similarity_threshold": 0.8,
        ...
    },
    "is_valid": true,
    "error_message": null
}
```

### Update Configuration
```http
POST /config/self-consistency
Content-Type: application/json

{
    "num_candidates": 7,
    "similarity_threshold": 0.85
}
```

Response:
```json
{
    "message": "Configuration updated successfully",
    "config": {
        "enable_self_consistency": true,
        "num_candidates": 7,
        "similarity_threshold": 0.85,
        ...
    },
    "is_valid": true
}
```

## Usage Examples

### Basic Usage
The self-consistency feature is automatically enabled. The chatbot will:
1. Generate 5 candidate responses
2. Cluster them by similarity
3. Select the majority response
4. Stream the result

### Disabling Self-Consistency
```python
from core.config import update_self_consistency_config

update_self_consistency_config(enable_self_consistency=False)
```

### Adjusting Parameters
```python
from core.config import update_self_consistency_config

# Increase number of candidates for better consistency
update_self_consistency_config(num_candidates=10)

# Adjust similarity threshold
update_self_consistency_config(similarity_threshold=0.85)
```

## Performance Considerations

### Response Time
- **With self-consistency**: ~3-5x longer than single response
- **Candidates**: 5-10 responses generated in parallel
- **Clustering**: Fast TF-IDF similarity calculation

### Resource Usage
- **Memory**: Additional storage for candidate responses
- **CPU**: Text similarity calculations
- **GPU**: Multiple LLM calls (if available)

### Optimization Tips
1. **Reduce candidates**: Lower `num_candidates` for faster responses
2. **Adjust threshold**: Higher threshold = fewer clusters = faster selection
3. **Disable variations**: Turn off temperature/prompt variations for speed

## Monitoring and Debugging

### Logging
The system provides comprehensive logging:
- Candidate generation progress
- Clustering information
- Selection metadata
- Error handling

### Debug Information
```python
# Enable debug logging
from core.config import update_self_consistency_config
update_self_consistency_config(enable_debug_logs=True)
```

### Response Metadata
Each response includes metadata about the selection process:
- Selection method used
- Number of clusters found
- Cluster sizes
- Similarity scores

## Error Handling

### Fallback Strategies
1. **No candidates generated**: Falls back to original single response
2. **Clustering fails**: Returns first candidate
3. **Selection fails**: Returns largest cluster's first response
4. **LLM errors**: Graceful degradation with error messages

### Common Issues
- **Timeout**: Increase `max_response_time`
- **Memory issues**: Reduce `num_candidates`
- **Poor clustering**: Adjust `similarity_threshold`

## Testing

### Unit Tests
```bash
# Run tests for self-consistency functions
python -m pytest tests/test_self_consistency.py
```

### Integration Tests
```bash
# Test with actual LLM calls
python -m pytest tests/test_integration.py
```

### Performance Tests
```bash
# Benchmark response times
python -m pytest tests/test_performance.py
```

## Future Enhancements

### Planned Features
1. **Adaptive clustering**: Dynamic similarity thresholds
2. **Response quality scoring**: Better selection criteria
3. **Caching**: Store common responses
4. **Parallel processing**: Faster candidate generation

### Research Directions
1. **Ensemble methods**: Combine multiple selection strategies
2. **Confidence scoring**: Measure response reliability
3. **Domain adaptation**: PMAY-specific optimizations

## Troubleshooting

### Common Problems

#### Slow Response Times
- Reduce `num_candidates`
- Disable `temperature_variation`
- Check LLM server performance

#### Poor Response Quality
- Increase `num_candidates`
- Adjust `similarity_threshold`
- Enable `prompt_variations`

#### Memory Issues
- Reduce `similarity_max_features`
- Lower `num_candidates`
- Monitor system resources

### Debug Commands
```python
# Check configuration
from core.config import get_self_consistency_config, validate_config
config = get_self_consistency_config()
is_valid, error = validate_config()
print(f"Config valid: {is_valid}, Error: {error}")

# Test similarity calculation
from core.llm import calculate_text_similarity
texts = ["Response 1", "Response 2", "Response 3"]
similarity = calculate_text_similarity(texts)
print(f"Similarity matrix: {similarity}")
```

## Contributing

When contributing to the self-consistency implementation:

1. **Follow the configuration pattern** for new parameters
2. **Add comprehensive logging** for debugging
3. **Include fallback strategies** for robustness
4. **Update this documentation** for new features
5. **Add tests** for new functionality

## References

- [Self-Consistency Improves Chain of Thought Reasoning in Language Models](https://arxiv.org/abs/2203.11171)
- [TF-IDF Vectorization](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- [Cosine Similarity](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html) 
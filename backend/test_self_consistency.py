#!/usr/bin/env python3
"""
Test script for self-consistency prompting implementation.
This script tests the core functionality without requiring the full API.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.llm import (
    calculate_text_similarity,
    cluster_similar_responses,
    select_majority_response,
    generate_candidate_responses,
    call_llm_with_self_consistency
)
from core.config import (
    SELF_CONSISTENCY_CONFIG,
    update_self_consistency_config,
    get_self_consistency_config,
    validate_config
)

def test_text_similarity():
    """Test text similarity calculation."""
    print("Testing text similarity calculation...")
    
    # Test case 1: Similar texts
    texts1 = [
        "The PMAY scheme provides housing assistance to eligible beneficiaries.",
        "PMAY offers housing support to qualified applicants.",
        "The Pradhan Mantri Awas Yojana helps people get homes."
    ]
    
    similarity_matrix = calculate_text_similarity(texts1)
    print(f"Similarity matrix for similar texts:\n{similarity_matrix}")
    
    # Test case 2: Different texts
    texts2 = [
        "The PMAY scheme provides housing assistance.",
        "The weather is sunny today.",
        "Python is a programming language."
    ]
    
    similarity_matrix2 = calculate_text_similarity(texts2)
    print(f"Similarity matrix for different texts:\n{similarity_matrix2}")
    
    # Test case 3: Empty and short texts
    texts3 = [
        "Short",
        "",
        "This is a longer text with more content."
    ]
    
    similarity_matrix3 = calculate_text_similarity(texts3)
    print(f"Similarity matrix for mixed texts:\n{similarity_matrix3}")
    
    print("✓ Text similarity tests completed\n")

def test_clustering():
    """Test response clustering."""
    print("Testing response clustering...")
    
    # Test responses with different similarity levels
    responses = [
        "PMAY provides housing assistance to eligible beneficiaries.",
        "The PMAY scheme offers housing support to qualified applicants.",
        "PMAY helps people get homes through government assistance.",
        "The weather is sunny today.",
        "Python is a programming language for developers."
    ]
    
    # Test different similarity thresholds
    thresholds = [0.5, 0.7, 0.9]
    
    for threshold in thresholds:
        clusters = cluster_similar_responses(responses, threshold)
        print(f"Clusters with threshold {threshold}: {clusters}")
        
        # Show which responses are in each cluster
        for i, cluster in enumerate(clusters):
            cluster_responses = [responses[idx] for idx in cluster]
            print(f"  Cluster {i}: {cluster_responses}")
    
    print("✓ Clustering tests completed\n")

def test_majority_selection():
    """Test majority response selection."""
    print("Testing majority response selection...")
    
    # Test case 1: Clear majority
    responses1 = [
        "PMAY provides housing assistance.",
        "PMAY offers housing support.",
        "PMAY helps with housing.",
        "The weather is sunny.",
        "Python is a language."
    ]
    
    clusters1 = cluster_similar_responses(responses1, 0.7)
    selected1, metadata1 = select_majority_response(responses1, clusters1)
    
    print(f"Test 1 - Selected: {selected1}")
    print(f"Test 1 - Metadata: {metadata1}")
    
    # Test case 2: No clear majority
    responses2 = [
        "Response A",
        "Response B",
        "Response C"
    ]
    
    clusters2 = cluster_similar_responses(responses2, 0.9)
    selected2, metadata2 = select_majority_response(responses2, clusters2)
    
    print(f"Test 2 - Selected: {selected2}")
    print(f"Test 2 - Metadata: {metadata2}")
    
    # Test case 3: Empty responses
    selected3, metadata3 = select_majority_response([], [])
    print(f"Test 3 - Selected: {selected3}")
    print(f"Test 3 - Metadata: {metadata3}")
    
    print("✓ Majority selection tests completed\n")

def test_configuration():
    """Test configuration management."""
    print("Testing configuration management...")
    
    # Get current configuration
    current_config = get_self_consistency_config()
    print(f"Current config: {current_config}")
    
    # Validate configuration
    is_valid, error = validate_config()
    print(f"Config valid: {is_valid}, Error: {error}")
    
    # Test configuration updates
    update_self_consistency_config(num_candidates=3, similarity_threshold=0.75)
    updated_config = get_self_consistency_config()
    print(f"Updated config: {updated_config}")
    
    # Test invalid configuration
    try:
        update_self_consistency_config(num_candidates=1)  # Should fail
        print("❌ Invalid config test failed - should have raised error")
    except Exception as e:
        print(f"✓ Invalid config test passed - caught error: {e}")
    
    # Restore original configuration
    update_self_consistency_config(num_candidates=5, similarity_threshold=0.8)
    
    print("✓ Configuration tests completed\n")

async def test_candidate_generation():
    """Test candidate response generation (requires LLM)."""
    print("Testing candidate response generation...")
    
    # Mock context and prompt for testing
    context = "PMAY is a government housing scheme that provides assistance to eligible beneficiaries."
    prompt = "What is PMAY?"
    system_prompt = "You are a helpful assistant that provides information about PMAY."
    
    try:
        # Test with reduced number of candidates for faster testing
        update_self_consistency_config(num_candidates=2)
        
        candidates = await generate_candidate_responses(
            context, prompt, system_prompt, num_candidates=2
        )
        
        print(f"Generated {len(candidates)} candidates:")
        for i, candidate in enumerate(candidates):
            print(f"  Candidate {i+1}: {candidate[:100]}...")
        
        if candidates:
            # Test clustering and selection
            clusters = cluster_similar_responses(candidates)
            selected, metadata = select_majority_response(candidates, clusters)
            
            print(f"Selected response: {selected[:100]}...")
            print(f"Selection metadata: {metadata}")
        
    except Exception as e:
        print(f"❌ Candidate generation test failed: {e}")
        print("This might be due to LLM server not running or other issues.")
    
    # Restore original configuration
    update_self_consistency_config(num_candidates=5)
    
    print("✓ Candidate generation tests completed\n")

async def test_full_pipeline():
    """Test the complete self-consistency pipeline."""
    print("Testing complete self-consistency pipeline...")
    
    context = "PMAY provides housing assistance to eligible beneficiaries."
    prompt = "How does PMAY help people?"
    system_prompt = "You are a helpful assistant that provides information about PMAY."
    
    try:
        # Enable self-consistency
        update_self_consistency_config(enable_self_consistency=True, num_candidates=2)
        
        print("Running self-consistency pipeline...")
        response_chunks = []
        
        async for chunk in call_llm_with_self_consistency(context, prompt, system_prompt):
            response_chunks.append(chunk)
            print(f"Received chunk: {chunk}")
        
        full_response = "".join(response_chunks)
        print(f"Full response: {full_response}")
        
    except Exception as e:
        print(f"❌ Full pipeline test failed: {e}")
        print("This might be due to LLM server not running or other issues.")
    
    # Restore original configuration
    update_self_consistency_config(enable_self_consistency=True, num_candidates=5)
    
    print("✓ Full pipeline tests completed\n")

def main():
    """Run all tests."""
    print("🧪 Self-Consistency Prompting Test Suite")
    print("=" * 50)
    
    # Run synchronous tests
    test_text_similarity()
    test_clustering()
    test_majority_selection()
    test_configuration()
    
    # Run asynchronous tests
    print("Running async tests (requires LLM server)...")
    asyncio.run(test_candidate_generation())
    asyncio.run(test_full_pipeline())
    
    print("🎉 All tests completed!")
    print("\nNote: Some tests may fail if the LLM server is not running.")
    print("To run the LLM server, ensure Ollama is running with the llama3.2:1b model.")

if __name__ == "__main__":
    main() 
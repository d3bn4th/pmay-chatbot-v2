#!/usr/bin/env python3
"""
Demonstration script for self-consistency prompting in the PMAY chatbot.
This script shows how to configure and use the self-consistency feature.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import (
    update_self_consistency_config,
    get_self_consistency_config,
    validate_config
)
from core.llm import call_llm_with_self_consistency

async def demo_basic_usage():
    """Demonstrate basic self-consistency usage."""
    print("🚀 Demo 1: Basic Self-Consistency Usage")
    print("-" * 50)
    
    context = """
    PMAY (Pradhan Mantri Awas Yojana) is a government housing scheme that provides:
    - Interest subsidy on home loans
    - Credit-linked subsidy for affordable housing
    - Support for construction of new houses
    - Assistance for renovation of existing houses
    """
    
    prompt = "What benefits does PMAY provide?"
    system_prompt = "You are a helpful assistant that provides accurate information about PMAY."
    
    print(f"Context: {context.strip()}")
    print(f"Question: {prompt}")
    print("\nGenerating response with self-consistency...")
    
    response_chunks = []
    async for chunk in call_llm_with_self_consistency(context, prompt, system_prompt):
        response_chunks.append(chunk)
        print(chunk, end="", flush=True)
    
    print("\n\n" + "="*50)

async def demo_configuration_changes():
    """Demonstrate different configuration settings."""
    print("⚙️ Demo 2: Configuration Changes")
    print("-" * 50)
    
    # Show current configuration
    current_config = get_self_consistency_config()
    print(f"Current configuration: {current_config}")
    
    # Test different settings
    configs_to_test = [
        {
            "name": "High Consistency (More Candidates)",
            "settings": {"num_candidates": 8, "similarity_threshold": 0.85}
        },
        {
            "name": "Fast Response (Fewer Candidates)",
            "settings": {"num_candidates": 3, "similarity_threshold": 0.7}
        },
        {
            "name": "Conservative Clustering",
            "settings": {"similarity_threshold": 0.9, "min_cluster_size": 3}
        }
    ]
    
    context = "PMAY provides housing assistance to eligible beneficiaries."
    prompt = "How does PMAY work?"
    system_prompt = "You are a helpful assistant that provides information about PMAY."
    
    for config_test in configs_to_test:
        print(f"\n📋 Testing: {config_test['name']}")
        print(f"Settings: {config_test['settings']}")
        
        # Update configuration
        update_self_consistency_config(**config_test['settings'])
        
        # Validate configuration
        is_valid, error = validate_config()
        if not is_valid:
            print(f"❌ Invalid configuration: {error}")
            continue
        
        print("Generating response...")
        response_chunks = []
        async for chunk in call_llm_with_self_consistency(context, prompt, system_prompt):
            response_chunks.append(chunk)
        
        full_response = "".join(response_chunks)
        print(f"Response: {full_response[:200]}...")
    
    # Restore default configuration
    update_self_consistency_config(
        num_candidates=5,
        similarity_threshold=0.8,
        min_cluster_size=2
    )
    
    print("\n" + "="*50)

async def demo_disable_self_consistency():
    """Demonstrate disabling self-consistency."""
    print("🔌 Demo 3: Disabling Self-Consistency")
    print("-" * 50)
    
    context = "PMAY is a government housing scheme."
    prompt = "What is PMAY?"
    system_prompt = "You are a helpful assistant."
    
    print("Testing with self-consistency disabled...")
    
    # Disable self-consistency
    update_self_consistency_config(enable_self_consistency=False)
    
    response_chunks = []
    async for chunk in call_llm_with_self_consistency(context, prompt, system_prompt):
        response_chunks.append(chunk)
        print(chunk, end="", flush=True)
    
    print("\n\nNote: This used the original single-response method.")
    
    # Re-enable self-consistency
    update_self_consistency_config(enable_self_consistency=True)
    
    print("\n" + "="*50)

async def demo_error_handling():
    """Demonstrate error handling and fallbacks."""
    print("🛡️ Demo 4: Error Handling and Fallbacks")
    print("-" * 50)
    
    # Test with invalid configuration
    print("Testing with invalid configuration...")
    try:
        update_self_consistency_config(num_candidates=1)  # Invalid
        print("❌ Should have failed validation")
    except Exception as e:
        print(f"✓ Caught validation error: {e}")
    
    # Test with edge cases
    print("\nTesting with edge cases...")
    
    # Empty context
    context = ""
    prompt = "What is PMAY?"
    system_prompt = "You are a helpful assistant."
    
    print("Testing with empty context...")
    response_chunks = []
    async for chunk in call_llm_with_self_consistency(context, prompt, system_prompt):
        response_chunks.append(chunk)
        print(chunk, end="", flush=True)
    
    print("\n\n" + "="*50)

def show_configuration_help():
    """Show help information about configuration."""
    print("📖 Configuration Help")
    print("-" * 50)
    
    print("""
Key Configuration Parameters:

1. enable_self_consistency (bool)
   - Enable or disable self-consistency prompting
   - Default: True

2. num_candidates (int)
   - Number of candidate responses to generate
   - Range: 2-10 (recommended: 5-7)
   - Default: 5

3. similarity_threshold (float)
   - Threshold for clustering similar responses
   - Range: 0.7-0.9 (recommended: 0.8)
   - Default: 0.8

4. min_cluster_size (int)
   - Minimum size for a cluster to be considered
   - Range: 1-5
   - Default: 2

5. temperature_variation (bool)
   - Whether to vary temperature across candidates
   - Default: True

6. prompt_variations (bool)
   - Whether to use different prompt formulations
   - Default: True

API Endpoints:
- GET /config/self-consistency - Get current configuration
- POST /config/self-consistency - Update configuration

Example API call:
curl -X POST http://localhost:8000/config/self-consistency \\
  -H "Content-Type: application/json" \\
  -d '{"num_candidates": 7, "similarity_threshold": 0.85}'
""")

async def main():
    """Run all demonstrations."""
    print("🎯 PMAY Chatbot Self-Consistency Demonstrations")
    print("=" * 60)
    
    try:
        # Run demonstrations
        await demo_basic_usage()
        await demo_configuration_changes()
        await demo_disable_self_consistency()
        await demo_error_handling()
        
        # Show help
        show_configuration_help()
        
        print("\n🎉 All demonstrations completed!")
        print("\nTo use self-consistency in your application:")
        print("1. Ensure the backend server is running")
        print("2. Configure settings via API or code")
        print("3. Use call_llm_with_self_consistency() function")
        print("4. Monitor logs for debugging information")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Make sure the LLM server (Ollama) is running with llama3.2:1b model.")

if __name__ == "__main__":
    asyncio.run(main()) 
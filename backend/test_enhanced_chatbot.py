#!/usr/bin/env python3
"""
Test script for the enhanced PMAY chatbot functionality.
Tests greeting caching and fallback mechanisms.
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BACKEND_URL = "http://localhost:8000"
TEST_MESSAGES = [
    # Greeting messages (should use cache)
    "Hello",
    "Hi there",
    "Good morning",
    "Namaste",
    "How are you?",
    "What can you do?",
    "Who are you?",
    
    # Ambiguous questions (should use fallback)
    "What is it?",
    "Tell me about this",
    "Help me",
    "Explain",
    
    # Valid PMAY questions (should use RAG)
    "What is PMAY?",
    "How to apply for PMAY?",
    "What are the eligibility criteria for PMAY?",
    "What documents are required for PMAY application?",
    
    # Questions that should trigger fallback (no relevant info)
    "What is the weather like?",
    "How to cook biryani?",
    "What is quantum physics?",
]

def test_greeting_cache():
    """Test greeting caching functionality."""
    print("🧪 Testing Greeting Cache Functionality")
    print("=" * 50)
    
    # Test cache stats before
    response = requests.get(f"{BACKEND_URL}/cache/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"Initial cache stats: {stats}")
    
    # Test greeting messages
    greeting_messages = ["Hello", "Hi", "Good morning", "Namaste"]
    
    for i, message in enumerate(greeting_messages, 1):
        print(f"\n{i}. Testing greeting: '{message}'")
        
        # First request (should not be cached)
        start_time = time.time()
        response = requests.post(f"{BACKEND_URL}/chat", 
                               json={"message": message},
                               headers={"Content-Type": "application/json"})
        first_response_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"   ✅ First response time: {first_response_time:.3f}s")
        else:
            print(f"   ❌ First request failed: {response.status_code}")
            continue
        
        # Second request (should be cached)
        start_time = time.time()
        response = requests.post(f"{BACKEND_URL}/chat", 
                               json={"message": message},
                               headers={"Content-Type": "application/json"})
        second_response_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"   ✅ Second response time: {second_response_time:.3f}s")
            if second_response_time < first_response_time * 0.5:  # Should be significantly faster
                print(f"   ✅ Cache working! Speed improvement: {first_response_time/second_response_time:.1f}x")
            else:
                print(f"   ⚠️  Cache may not be working optimally")
        else:
            print(f"   ❌ Second request failed: {response.status_code}")
    
    # Test cache stats after
    response = requests.get(f"{BACKEND_URL}/cache/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"\nFinal cache stats: {stats}")

def test_fallback_mechanism():
    """Test fallback mechanism for various scenarios."""
    print("\n🛡️  Testing Fallback Mechanism")
    print("=" * 50)
    
    # Test ambiguous questions
    ambiguous_questions = [
        "What is it?",
        "Tell me about this",
        "Help me",
        "Explain",
        "How?",
        "What?"
    ]
    
    print("\n1. Testing Ambiguous Questions:")
    for i, question in enumerate(ambiguous_questions, 1):
        print(f"\n   {i}. Testing: '{question}'")
        response = requests.post(f"{BACKEND_URL}/chat", 
                               json={"message": question},
                               headers={"Content-Type": "application/json"})
        
        if response.status_code == 200:
            print(f"   ✅ Response received")
            # Check if response contains fallback indicators
            content = response.text
            if "unclear" in content.lower() or "clarify" in content.lower() or "specific" in content.lower():
                print(f"   ✅ Fallback response detected")
            else:
                print(f"   ⚠️  May not be using fallback")
        else:
            print(f"   ❌ Request failed: {response.status_code}")
    
    # Test questions that should trigger no-documents fallback
    no_docs_questions = [
        "What is the weather like?",
        "How to cook biryani?",
        "What is quantum physics?",
        "Tell me about dinosaurs"
    ]
    
    print("\n2. Testing No-Documents Fallback:")
    for i, question in enumerate(no_docs_questions, 1):
        print(f"\n   {i}. Testing: '{question}'")
        response = requests.post(f"{BACKEND_URL}/chat", 
                               json={"message": question},
                               headers={"Content-Type": "application/json"})
        
        if response.status_code == 200:
            print(f"   ✅ Response received")
            content = response.text
            if "couldn't find" in content.lower() or "don't have" in content.lower() or "knowledge base" in content.lower():
                print(f"   ✅ No-documents fallback detected")
            else:
                print(f"   ⚠️  May not be using no-documents fallback")
        else:
            print(f"   ❌ Request failed: {response.status_code}")

def test_valid_pmay_questions():
    """Test valid PMAY questions that should use RAG."""
    print("\n📚 Testing Valid PMAY Questions (RAG)")
    print("=" * 50)
    
    valid_questions = [
        "What is PMAY?",
        "How to apply for PMAY?",
        "What are the eligibility criteria for PMAY?",
        "What documents are required for PMAY application?"
    ]
    
    for i, question in enumerate(valid_questions, 1):
        print(f"\n{i}. Testing: '{question}'")
        response = requests.post(f"{BACKEND_URL}/chat", 
                               json={"message": question},
                               headers={"Content-Type": "application/json"})
        
        if response.status_code == 200:
            print(f"   ✅ Response received")
            content = response.text
            # Check if response contains PMAY-related content
            if "pmay" in content.lower() or "pradhan mantri" in content.lower() or "awas yojana" in content.lower():
                print(f"   ✅ PMAY-related response detected")
            else:
                print(f"   ⚠️  Response may not be PMAY-related")
        else:
            print(f"   ❌ Request failed: {response.status_code}")

def test_cache_management():
    """Test cache management endpoints."""
    print("\n🔧 Testing Cache Management")
    print("=" * 50)
    
    # Test cache stats
    print("1. Testing cache stats endpoint:")
    response = requests.get(f"{BACKEND_URL}/cache/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"   ✅ Cache stats: {stats}")
    else:
        print(f"   ❌ Cache stats failed: {response.status_code}")
    
    # Test cache clear
    print("\n2. Testing cache clear endpoint:")
    response = requests.delete(f"{BACKEND_URL}/cache/clear")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Cache cleared: {result}")
    else:
        print(f"   ❌ Cache clear failed: {response.status_code}")
    
    # Test cache stats after clear
    print("\n3. Testing cache stats after clear:")
    response = requests.get(f"{BACKEND_URL}/cache/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"   ✅ Cache stats after clear: {stats}")
    else:
        print(f"   ❌ Cache stats failed: {response.status_code}")

def test_health_check():
    """Test health check endpoint."""
    print("\n🏥 Testing Health Check")
    print("=" * 50)
    
    response = requests.get(f"{BACKEND_URL}/health")
    if response.status_code == 200:
        health = response.json()
        print(f"   ✅ Health check passed: {health}")
    else:
        print(f"   ❌ Health check failed: {response.status_code}")

def run_comprehensive_test():
    """Run all tests."""
    print("🚀 Starting Comprehensive PMAY Chatbot Enhancement Tests")
    print("=" * 60)
    
    try:
        # Test health check first
        test_health_check()
        
        # Test core functionality
        test_greeting_cache()
        test_fallback_mechanism()
        test_valid_pmay_questions()
        
        # Test management endpoints
        test_cache_management()
        
        print("\n🎉 All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the backend server.")
        print("   Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")

if __name__ == "__main__":
    run_comprehensive_test() 
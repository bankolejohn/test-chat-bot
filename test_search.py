#!/usr/bin/env python3
"""
Test script for knowledge base search functionality
"""

import json
from app import search_knowledge_base, load_knowledge_base, get_enhanced_mock_response

def test_search_function():
    """Test the search function with various queries"""
    print("🔍 Testing Knowledge Base Search Function")
    print("=" * 50)
    
    # Load knowledge base
    knowledge_base = load_knowledge_base()
    
    # Test queries
    test_queries = [
        "Why is my dashboard score different?",
        "When does the program end?",
        "Can I change my course?",
        "What financial support is available?",
        "How do I contact support?",
        "What is 3MTT about?",
        "Random unrelated question"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 30)
        
        # Test search function
        results = search_knowledge_base(query, knowledge_base)
        print(f"Search results ({len(results)} found):")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result}")
        
        # Test enhanced mock response
        response = get_enhanced_mock_response(query)
        print(f"\nBot Response:")
        print(f"  {response[:100]}{'...' if len(response) > 100 else ''}")
        print("\n" + "="*50)

if __name__ == "__main__":
    test_search_function()
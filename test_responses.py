#!/usr/bin/env python3
"""
Test the chatbot responses to ensure they're working correctly
"""

from app import get_enhanced_mock_response

def test_chatbot_responses():
    """Test various user queries"""
    print("🤖 Testing Chatbot Responses")
    print("=" * 50)
    
    test_cases = [
        "Why is my dashboard score different from Darey.io?",
        "When does cohort 3 end?",
        "Can I change my course after starting?",
        "What financial support do you provide?",
        "How can I contact support?",
        "What courses are available?",
        "Tell me about 3MTT program",
        "I'm having trouble logging in",
        "What is the weather today?"  # Unrelated question
    ]
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n{i}. User: {query}")
        print("-" * 40)
        response = get_enhanced_mock_response(query)
        print(f"Bot: {response}")
        print("\n" + "="*50)

if __name__ == "__main__":
    test_chatbot_responses()
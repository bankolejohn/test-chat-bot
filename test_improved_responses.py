#!/usr/bin/env python3
"""
Test the improved chatbot responses for coherence and intelligence
"""

from app import get_enhanced_mock_response, get_ai_response, load_knowledge_base

def test_improved_chatbot():
    """Test various scenarios to ensure coherent responses"""
    print("🧠 Testing Improved Chatbot Intelligence")
    print("=" * 60)
    
    test_scenarios = [
        {
            "category": "Program Information",
            "queries": [
                "What is 3MTT about?",
                "Tell me about the program phases",
                "How many people are in phase 1?"
            ]
        },
        {
            "category": "Technical Support", 
            "queries": [
                "I can't log into my account",
                "My dashboard scores are different",
                "I'm having trouble accessing the platform"
            ]
        },
        {
            "category": "Course Management",
            "queries": [
                "What courses do you offer?",
                "Can I switch my course?",
                "What tracks are available?"
            ]
        },
        {
            "category": "Support & Contact",
            "queries": [
                "How do I contact support?",
                "What are your office hours?",
                "I need help with something"
            ]
        },
        {
            "category": "Financial & Logistics",
            "queries": [
                "What financial support is available?",
                "Do I need to pay for anything?",
                "What about transportation costs?"
            ]
        },
        {
            "category": "Edge Cases",
            "queries": [
                "What's the weather like?",
                "How do I cook rice?",
                "Random unrelated question"
            ]
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📋 {scenario['category']}")
        print("-" * 40)
        
        for i, query in enumerate(scenario['queries'], 1):
            print(f"\n{i}. User: {query}")
            response = get_enhanced_mock_response(query)
            
            # Analyze response quality
            is_coherent = len(response.split()) > 5 and not response.startswith("Based on our knowledge base:")
            is_helpful = any(word in response.lower() for word in ['help', 'support', 'information', 'program', '3mtt'])
            
            print(f"   Bot: {response}")
            print(f"   Quality: {'✅ Coherent' if is_coherent else '❌ Fragmented'} | {'✅ Helpful' if is_helpful else '❌ Generic'}")
        
        print("\n" + "="*60)

def test_with_ai_if_available():
    """Test with actual AI if API key is available"""
    import os
    if os.getenv('OPENAI_API_KEY'):
        print("\n🤖 Testing with OpenAI API")
        print("-" * 30)
        
        test_query = "Tell me about the 3MTT program and its phases"
        ai_response = get_ai_response(test_query)
        print(f"Query: {test_query}")
        print(f"AI Response: {ai_response}")
    else:
        print("\n💡 No OpenAI API key found - using enhanced mock responses only")

if __name__ == "__main__":
    test_improved_chatbot()
    test_with_ai_if_available()
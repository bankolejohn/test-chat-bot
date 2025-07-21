#!/usr/bin/env python3
"""
Training script for the 3MTT AI Chatbot
This script helps improve the chatbot by analyzing feedback and updating the knowledge base
"""

import json
import os
from datetime import datetime
from collections import Counter

def load_data():
    """Load all data files"""
    try:
        with open('conversations.json', 'r') as f:
            conversations = json.load(f)
    except FileNotFoundError:
        conversations = []
    
    try:
        with open('training_data.json', 'r') as f:
            training_data = json.load(f)
    except FileNotFoundError:
        training_data = {"training_examples": [], "feedback_data": [], "improvement_suggestions": []}
    
    try:
        with open('knowledge_base.json', 'r') as f:
            knowledge_base = json.load(f)
    except FileNotFoundError:
        knowledge_base = {}
    
    return conversations, training_data, knowledge_base

def analyze_conversations():
    """Analyze conversation patterns and identify improvement areas"""
    conversations, training_data, knowledge_base = load_data()
    
    print("=== CONVERSATION ANALYSIS ===")
    print(f"Total conversations: {len(conversations)}")
    
    # Sentiment analysis
    sentiment_counts = Counter(conv.get('sentiment', 'neutral') for conv in conversations)
    print(f"Sentiment distribution: {dict(sentiment_counts)}")
    
    # Common topics
    all_messages = [conv.get('user_message', '').lower() for conv in conversations]
    common_words = Counter()
    for message in all_messages:
        words = message.split()
        common_words.update(word for word in words if len(word) > 3)
    
    print(f"Top 10 topics: {common_words.most_common(10)}")
    
    # Feedback analysis
    feedback_data = training_data.get('feedback_data', [])
    if feedback_data:
        helpful_count = sum(1 for f in feedback_data if f.get('helpful', True))
        print(f"Feedback: {helpful_count}/{len(feedback_data)} responses marked as helpful")
        
        # Identify problematic responses
        unhelpful_responses = [f for f in feedback_data if not f.get('helpful', True)]
        if unhelpful_responses:
            print("\nProblematic responses that need improvement:")
            for resp in unhelpful_responses[-5:]:  # Last 5
                print(f"- User: {resp.get('user_message', '')[:50]}...")
                print(f"  Bot: {resp.get('bot_response', '')[:50]}...")
    
    return conversations, training_data, knowledge_base

def suggest_knowledge_improvements(conversations, training_data, knowledge_base):
    """Suggest improvements to the knowledge base"""
    print("\n=== KNOWLEDGE BASE IMPROVEMENT SUGGESTIONS ===")
    
    # Find frequently asked questions not well covered
    all_messages = [conv.get('user_message', '').lower() for conv in conversations]
    
    # Common question patterns
    question_patterns = {
        'course': ['course', 'track', 'program', 'study'],
        'timeline': ['when', 'time', 'date', 'deadline', 'end'],
        'technical': ['dashboard', 'login', 'access', 'error', 'problem'],
        'support': ['help', 'contact', 'support', 'assistance'],
        'assessment': ['test', 'exam', 'assessment', 'evaluation'],
        'financial': ['cost', 'fee', 'payment', 'money', 'financial']
    }
    
    topic_counts = {}
    for topic, keywords in question_patterns.items():
        count = sum(1 for message in all_messages 
                   if any(keyword in message for keyword in keywords))
        topic_counts[topic] = count
    
    print("Question topic frequency:")
    for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"- {topic}: {count} questions")
    
    # Suggest new knowledge base entries
    suggestions = []
    
    if topic_counts.get('technical', 0) > 5:
        suggestions.append({
            "section": "troubleshooting",
            "content": "Add more technical troubleshooting guides for common dashboard and login issues"
        })
    
    if topic_counts.get('timeline', 0) > 3:
        suggestions.append({
            "section": "timeline",
            "content": "Add more detailed timeline information and important dates"
        })
    
    # Save suggestions
    training_data['improvement_suggestions'] = suggestions
    with open('training_data.json', 'w') as f:
        json.dump(training_data, f, indent=2)
    
    print(f"\nGenerated {len(suggestions)} improvement suggestions")
    return suggestions

def create_training_examples():
    """Create new training examples from successful conversations"""
    conversations, training_data, knowledge_base = load_data()
    
    print("\n=== CREATING TRAINING EXAMPLES ===")
    
    # Find conversations with positive sentiment that could be training examples
    positive_conversations = [
        conv for conv in conversations 
        if conv.get('sentiment') == 'positive' and len(conv.get('user_message', '')) > 10
    ]
    
    new_examples = []
    for conv in positive_conversations[-10:]:  # Last 10 positive conversations
        example = {
            "user_input": conv.get('user_message', ''),
            "expected_response": conv.get('bot_response', ''),
            "category": "user_generated",
            "keywords": conv.get('user_message', '').lower().split()[:5],
            "timestamp": conv.get('timestamp', ''),
            "sentiment": conv.get('sentiment', 'positive')
        }
        new_examples.append(example)
    
    # Add to training data
    training_data['training_examples'].extend(new_examples)
    
    # Remove duplicates
    seen = set()
    unique_examples = []
    for example in training_data['training_examples']:
        key = example['user_input']
        if key not in seen:
            seen.add(key)
            unique_examples.append(example)
    
    training_data['training_examples'] = unique_examples
    
    with open('training_data.json', 'w') as f:
        json.dump(training_data, f, indent=2)
    
    print(f"Added {len(new_examples)} new training examples")
    print(f"Total training examples: {len(unique_examples)}")

def generate_report():
    """Generate a comprehensive training report"""
    conversations, training_data, knowledge_base = load_data()
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "statistics": {
            "total_conversations": len(conversations),
            "total_training_examples": len(training_data.get('training_examples', [])),
            "total_feedback": len(training_data.get('feedback_data', [])),
            "knowledge_base_sections": len(knowledge_base)
        },
        "sentiment_analysis": {},
        "improvement_areas": [],
        "recommendations": []
    }
    
    # Sentiment analysis
    sentiment_counts = Counter(conv.get('sentiment', 'neutral') for conv in conversations)
    report["sentiment_analysis"] = dict(sentiment_counts)
    
    # Calculate satisfaction rate
    feedback_data = training_data.get('feedback_data', [])
    if feedback_data:
        helpful_count = sum(1 for f in feedback_data if f.get('helpful', True))
        satisfaction_rate = (helpful_count / len(feedback_data)) * 100
        report["statistics"]["satisfaction_rate"] = f"{satisfaction_rate:.1f}%"
    
    # Recommendations
    if sentiment_counts.get('negative', 0) > sentiment_counts.get('positive', 0):
        report["recommendations"].append("Focus on improving response quality - more negative than positive sentiment")
    
    if len(training_data.get('feedback_data', [])) < 10:
        report["recommendations"].append("Encourage more user feedback to improve training data")
    
    # Save report
    with open(f'training_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n=== TRAINING REPORT ===")
    print(json.dumps(report, indent=2))

def main():
    """Main training function"""
    print("🤖 3MTT Chatbot Training System")
    print("=" * 40)
    
    # Analyze current performance
    conversations, training_data, knowledge_base = analyze_conversations()
    
    # Suggest improvements
    suggestions = suggest_knowledge_improvements(conversations, training_data, knowledge_base)
    
    # Create new training examples
    create_training_examples()
    
    # Generate comprehensive report
    generate_report()
    
    print("\n✅ Training analysis complete!")
    print("Check the generated training report for detailed insights.")

if __name__ == "__main__":
    main()
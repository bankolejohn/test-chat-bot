#!/usr/bin/env python3
"""
Example script to add new knowledge to the knowledge base
"""

import json

def add_application_process_info():
    """Add application process information to knowledge base"""
    
    # Load existing knowledge base
    with open('knowledge_base.json', 'r') as f:
        knowledge_base = json.load(f)
    
    # Add new section
    knowledge_base['application_process'] = {
        "eligibility": "Nigerian citizens aged 18-35 with basic digital literacy",
        "steps": "Online application → Assessment → Selection → Onboarding",
        "required_documents": ["Valid ID", "Educational certificates", "Passport photograph"],
        "deadlines": "Applications typically open quarterly",
        "selection_criteria": "Based on assessment scores, location, and track preference"
    }
    
    # Save updated knowledge base
    with open('knowledge_base.json', 'w') as f:
        json.dump(knowledge_base, f, indent=2)
    
    print("✅ Added application process information to knowledge base")

def add_course_details():
    """Add detailed course information"""
    
    with open('knowledge_base.json', 'r') as f:
        knowledge_base = json.load(f)
    
    # Expand existing courses section
    knowledge_base['courses']['software_development'] = {
        "duration": "6 months intensive training",
        "prerequisites": "Basic computer skills, logical thinking",
        "curriculum": ["HTML/CSS", "JavaScript", "Python/Java", "Database management"],
        "career_outcomes": "Full-stack developer, Frontend developer, Backend developer"
    }
    
    knowledge_base['courses']['cybersecurity'] = {
        "duration": "6 months intensive training",
        "prerequisites": "Basic IT knowledge, attention to detail",
        "curriculum": ["Network Security", "Ethical Hacking", "Risk Assessment"],
        "career_outcomes": "Security Analyst, Penetration Tester, Security Consultant"
    }
    
    with open('knowledge_base.json', 'w') as f:
        json.dump(knowledge_base, f, indent=2)
    
    print("✅ Added detailed course information to knowledge base")

if __name__ == "__main__":
    print("🔧 Expanding 3MTT Knowledge Base")
    add_application_process_info()
    add_course_details()
    print("🎉 Knowledge base expansion complete!")
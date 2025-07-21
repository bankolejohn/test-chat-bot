#!/usr/bin/env python3
"""
Setup script for 3MTT AI Chatbot
"""

import os
import json
import subprocess
import sys

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        print("Creating .env file...")
        with open('.env', 'w') as f:
            f.write("""# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Flask Configuration  
SECRET_KEY=your_secret_key_for_sessions
FLASK_ENV=development

# AI Model Settings
AI_MODEL=gpt-4
MAX_TOKENS=300
TEMPERATURE=0.7
""")
        print("✅ Created .env file - please add your OpenAI API key")
    else:
        print("✅ .env file already exists")

def install_requirements():
    """Install Python requirements"""
    print("Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False
    return True

def initialize_data_files():
    """Initialize data files if they don't exist"""
    files_to_check = [
        ('conversations.json', []),
        ('training_data.json', {
            "training_examples": [],
            "feedback_data": [],
            "improvement_suggestions": []
        })
    ]
    
    for filename, default_content in files_to_check:
        if not os.path.exists(filename):
            print(f"Creating {filename}...")
            with open(filename, 'w') as f:
                json.dump(default_content, f, indent=2)
            print(f"✅ Created {filename}")
        else:
            print(f"✅ {filename} already exists")

def main():
    """Main setup function"""
    print("🤖 3MTT AI Chatbot Setup")
    print("=" * 30)
    
    # Install requirements
    if not install_requirements():
        return
    
    # Create environment file
    create_env_file()
    
    # Initialize data files
    initialize_data_files()
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run: python app.py")
    print("3. Open: http://localhost:5000")
    print("4. Admin panel: http://localhost:5000/admin/analytics")
    print("5. Knowledge base: http://localhost:5000/admin/knowledge")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Simplified Flask app for Elastic Beanstalk
"""

import os
import requests
import json
from flask import Flask, request, jsonify, render_template_string

# Create Flask app
application = Flask(__name__)
application.secret_key = os.environ.get('SECRET_KEY', 'eb-secret-key')

# Configuration
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
AI_MODEL = os.environ.get('AI_MODEL', 'deepseek/deepseek-r1:free')

# Mock responses
MOCK_RESPONSES = {
    "dashboard_scores": "This is because your dashboard gradually syncs with your Darey.io and it may take some time for your Darey.io score to tally with that of your dashboard.",
    "program_end": "Cohort 3 ends July 20th.",
    "change_course": "Yes, you can change your course before you get admitted into the Learning Management System. Once you have been admitted, you won't be able to change your course. You can change your location at any given during cohort 3.",
    "default": "Hello! Welcome to 3MTT support. How can I help you today?"
}

def get_openrouter_response(message):
    """Get response from OpenRouter API"""
    if not OPENROUTER_API_KEY:
        raise Exception("No API key")
    
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://3mtt-chatbot.com",
            "X-Title": "3MTT Chatbot",
        },
        json={
            "model": AI_MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful customer support assistant for 3MTT organization. Keep responses concise and professional."},
                {"role": "user", "content": message}
            ],
            "max_tokens": 300,
            "temperature": 0.7
        },
        timeout=30
    )
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        raise Exception(f"API error: {response.status_code}")

def get_mock_response(message):
    """Get mock response"""
    message_lower = message.lower()
    if "dashboard" in message_lower or "score" in message_lower:
        return MOCK_RESPONSES["dashboard_scores"]
    elif "end" in message_lower or "cohort" in message_lower:
        return MOCK_RESPONSES["program_end"]
    elif "change" in message_lower or "course" in message_lower:
        return MOCK_RESPONSES["change_course"]
    else:
        return MOCK_RESPONSES["default"]

@application.route('/')
def index():
    """Chat interface"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>3MTT Support Chat</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .container { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; margin-bottom: 20px; }
            #chat { border: 1px solid #ddd; height: 400px; overflow-y: scroll; padding: 15px; margin-bottom: 15px; background: #f9f9f9; border-radius: 5px; }
            .message { margin: 10px 0; padding: 10px; border-radius: 8px; }
            .user { background: #007bff; color: white; text-align: right; margin-left: 20%; }
            .bot { background: #e9ecef; color: #333; margin-right: 20%; }
            .input-group { display: flex; gap: 10px; }
            #message-input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
            #send-button { padding: 12px 24px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
            #send-button:hover { background: #0056b3; }
            .status { padding: 10px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; margin-bottom: 15px; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 3MTT Support Chatbot</h1>
            <div class="status">
                Status: {{ "✅ DeepSeek AI Ready" if api_key else "⚠️ Using Mock Responses" }}<br>
                Model: {{ model }}
            </div>
            <div id="chat"></div>
            <div class="input-group">
                <input type="text" id="message-input" placeholder="Ask about 3MTT program..." onkeypress="handleKeyPress(event)">
                <button id="send-button" onclick="sendMessage()">Send</button>
            </div>
        </div>

        <script>
            function addMessage(message, isUser) {
                const chat = document.getElementById('chat');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + (isUser ? 'user' : 'bot');
                messageDiv.textContent = message;
                chat.appendChild(messageDiv);
                chat.scrollTop = chat.scrollHeight;
            }

            function sendMessage() {
                const input = document.getElementById('message-input');
                const message = input.value.trim();
                if (!message) return;

                addMessage(message, true);
                input.value = '';

                fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                })
                .then(response => response.json())
                .then(data => addMessage(data.response, false))
                .catch(error => addMessage('Error: ' + error.message, false));
            }

            function handleKeyPress(event) {
                if (event.key === 'Enter') sendMessage();
            }

            // Welcome message
            addMessage('Hello! Welcome to 3MTT support. Ask me about office hours, program timeline, or course changes.', false);
        </script>
    </body>
    </html>
    ''', api_key=bool(OPENROUTER_API_KEY), model=AI_MODEL)

@application.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Try AI first, fallback to mock
        try:
            if OPENROUTER_API_KEY:
                response = get_openrouter_response(message)
            else:
                response = get_mock_response(message)
        except Exception as e:
            print(f"AI Error: {e}")
            response = get_mock_response(message)
        
        return jsonify({'response': response})
        
    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({'error': str(e)}), 500

@application.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'ai_provider': 'openrouter' if OPENROUTER_API_KEY else 'mock',
        'model': AI_MODEL
    })

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
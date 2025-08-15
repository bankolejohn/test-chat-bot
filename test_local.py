#!/usr/bin/env python3
"""Simple local test script for the chatbot"""

import os
from flask import Flask, request, jsonify, render_template_string
import requests
import json

app = Flask(__name__)
app.secret_key = 'test-secret-key'

# Configuration
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
AI_MODEL = os.environ.get('AI_MODEL', 'deepseek/deepseek-r1:free')
AI_PROVIDER = os.environ.get('AI_PROVIDER', 'openrouter')

# Mock responses
MOCK_RESPONSES = {
    "dashboard_scores": "This is because your dashboard gradually syncs with your Darey.io and it may take some time for your Darey.io score to tally with that of your dashboard.",
    "program_end": "Cohort 3 ends July 20th.",
    "default": "Hello! Welcome to 3MTT support. How can I help you today?"
}

def get_openrouter_response(message):
    """Get response from OpenRouter API"""
    if not OPENROUTER_API_KEY:
        raise Exception("No OpenRouter API key")
    
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "3MTT Chatbot Test",
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
        raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")

def get_mock_response(message):
    """Get mock response"""
    message_lower = message.lower()
    if "dashboard" in message_lower or "score" in message_lower:
        return MOCK_RESPONSES["dashboard_scores"]
    elif "end" in message_lower or "cohort" in message_lower:
        return MOCK_RESPONSES["program_end"]
    else:
        return MOCK_RESPONSES["default"]

@app.route('/')
def index():
    """Simple chat interface"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>3MTT Test Chat</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
            #chat { border: 1px solid #ddd; height: 400px; overflow-y: scroll; padding: 10px; margin-bottom: 10px; }
            .message { margin: 10px 0; padding: 8px; border-radius: 5px; }
            .user { background-color: #e3f2fd; text-align: right; }
            .bot { background-color: #f5f5f5; }
            #input-container { display: flex; }
            #message-input { flex: 1; padding: 10px; border: 1px solid #ddd; }
            #send-button { padding: 10px 20px; background-color: #007bff; color: white; border: none; cursor: pointer; }
            .status { padding: 10px; background: #fff3cd; border: 1px solid #ffeaa7; margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <h1>3MTT Chatbot Test</h1>
        <div class="status">
            AI Provider: {{ ai_provider }}<br>
            API Key: {{ "✓ Set" if api_key else "✗ Not Set" }}<br>
            Model: {{ model }}
        </div>
        <div id="chat"></div>
        <div id="input-container">
            <input type="text" id="message-input" placeholder="Type your message..." onkeypress="handleKeyPress(event)">
            <button id="send-button" onclick="sendMessage()">Send</button>
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

            addMessage('Hello! Test the 3MTT chatbot. Try: "What are your office hours?" or "When does cohort 3 end?"', false);
        </script>
    </body>
    </html>
    ''', ai_provider=AI_PROVIDER, api_key=bool(OPENROUTER_API_KEY), model=AI_MODEL)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Try AI providers in order
        try:
            if AI_PROVIDER == 'openrouter' and OPENROUTER_API_KEY:
                response = get_openrouter_response(message)
                print(f"✓ Used OpenRouter: {response[:50]}...")
            else:
                response = get_mock_response(message)
                print(f"✓ Used Mock: {response[:50]}...")
        except Exception as e:
            print(f"✗ AI Error: {e}")
            response = get_mock_response(message)
            print(f"✓ Fallback to Mock: {response[:50]}...")
        
        return jsonify({'response': response})
        
    except Exception as e:
        print(f"✗ Chat Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting 3MTT Chatbot Test Server")
    print(f"AI Provider: {AI_PROVIDER}")
    print(f"OpenRouter Key: {'✓ Set' if OPENROUTER_API_KEY else '✗ Not Set'}")
    print(f"Model: {AI_MODEL}")
    print("Open: http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
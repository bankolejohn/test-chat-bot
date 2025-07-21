from flask import Flask, request, jsonify, render_template_string, session
import json
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Mock responses for 3MTT organization
MOCK_RESPONSES = {
    "dashboard_scores": "This is because your dashboard gradually syncs with your Darey.io and it may take some time for your Darey.io score to tally with that of your dashboard.",
    "program_end": "Cohort 3 ends July 20th.",
    "change_course": "Yes, you can change your course before you get admitted into the Learning Management System. Once you have been admitted, you won't be able to change your course. You can change your location at any given during cohort 3.",
    "onboarding_wait": "You will be added to communities where you will get access to free resources, collaborative self paced learning and physical meetup with your peers.",
    "entry_assessment": "Yes, there will be an entry assessment to determine the skill benchmark for each applicant. This will also be used in selecting the most applicable course for fellows.",
    "financial_support": "The only financial support for this phase of the programme will be the cost of training. Participants will be responsible for transportation, meals and other costs.",
    "physical_attendance": "The training is hybrid, meaning that it combines online and in-person components. While the majority of the training can be done remotely, there are aspects that will require in-person training.",
    "learning_community": "When you are assigned to a learning community in your location, the information will be displayed on your community page with the 3mtt portal when you log in.",
    "office hours": "Our office hours are Monday-Friday 9AM-6PM EST. We're closed on weekends and holidays.",
    "contact": "You can contact our support team for any 3MTT related inquiries.",
    "default": "Hello! Welcome to 3MTT support. How can I help you today? You can ask about dashboard scores, program timeline, course changes, assessments, or general support."
}

def get_ai_response(message, conversation_history=None):
    """Get response from OpenAI API with conversation context"""
    try:
        import openai
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return get_mock_response(message)
        
        client = openai.OpenAI(api_key=api_key)
        
        # Build conversation context
        messages = [
            {"role": "system", "content": """You are a helpful customer support assistant for 3MTT (3 Million Technical Talent) organization. 
            
            Key information about 3MTT:
            - It's a skills development program
            - Uses Darey.io platform for learning
            - Has dashboard score syncing
            - Cohort 3 ends July 20th
            - Hybrid training (online + in-person)
            - Entry assessments determine skill levels
            - Course changes allowed before LMS admission
            
            Keep responses concise, professional, and helpful. If you don't know something specific about 3MTT, acknowledge it and offer to connect them with support."""}
        ]
        
        # Add recent conversation history for context
        if conversation_history:
            for conv in conversation_history[-5:]:  # Last 5 exchanges
                messages.append({"role": "user", "content": conv.get("user_message", "")})
                messages.append({"role": "assistant", "content": conv.get("bot_response", "")})
        
        messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model=os.getenv('AI_MODEL', 'gpt-4'),
            messages=messages,
            max_tokens=int(os.getenv('MAX_TOKENS', '200')),
            temperature=float(os.getenv('TEMPERATURE', '0.7'))
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI Error: {e}")
        return get_mock_response(message)

def get_mock_response(message):
    """Return appropriate mock response based on message content"""
    message_lower = message.lower()
    if any(word in message_lower for word in ["dashboard", "score", "darey", "sync", "different"]):
        return MOCK_RESPONSES["dashboard_scores"]
    elif any(word in message_lower for word in ["change", "course", "location"]) and not any(word in message_lower for word in ["end", "finish"]):
        return MOCK_RESPONSES["change_course"]
    elif any(word in message_lower for word in ["onboard", "waiting", "wait"]):
        return MOCK_RESPONSES["onboarding_wait"]
    elif any(word in message_lower for word in ["assessment", "entry", "test", "exam"]):
        return MOCK_RESPONSES["entry_assessment"]
    elif any(word in message_lower for word in ["financial", "transport", "meal", "money"]):
        return MOCK_RESPONSES["financial_support"]
    elif any(word in message_lower for word in ["physical", "attendance", "mandatory", "person"]):
        return MOCK_RESPONSES["physical_attendance"]
    elif any(word in message_lower for word in ["community", "learning"]):
        return MOCK_RESPONSES["learning_community"]
    elif any(word in message_lower for word in ["end", "finish", "cohort", "program", "when"]):
        return MOCK_RESPONSES["program_end"]
    elif any(word in message_lower for word in ["hours", "time", "open", "close"]):
        return MOCK_RESPONSES["office hours"]
    elif any(word in message_lower for word in ["contact", "phone", "email", "support"]):
        return MOCK_RESPONSES["contact"]
    else:
        return MOCK_RESPONSES["default"]

def analyze_sentiment(message):
    """Basic sentiment analysis"""
    positive_words = ['good', 'great', 'excellent', 'happy', 'satisfied', 'thank', 'thanks', 'helpful']
    negative_words = ['bad', 'terrible', 'awful', 'angry', 'frustrated', 'disappointed', 'problem', 'issue', 'error']
    
    message_lower = message.lower()
    positive_count = sum(1 for word in positive_words if word in message_lower)
    negative_count = sum(1 for word in negative_words if word in message_lower)
    
    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"

def save_conversation(user_message, bot_response, session_id=None):
    """Save conversation to JSON file with enhanced metadata"""
    conversation = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id or "anonymous",
        "user_message": user_message,
        "bot_response": bot_response,
        "sentiment": analyze_sentiment(user_message),
        "message_length": len(user_message)
    }
    
    try:
        with open('conversations.json', 'r') as f:
            conversations = json.load(f)
    except FileNotFoundError:
        conversations = []
    
    conversations.append(conversation)
    
    with open('conversations.json', 'w') as f:
        json.dump(conversations, f, indent=2)

@app.route('/')
def index():
    """Serve the chat interface"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>3MTT Support Chat</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
            #chat-container { border: 1px solid #ddd; height: 400px; overflow-y: scroll; padding: 10px; margin-bottom: 10px; }
            .message { margin: 10px 0; padding: 8px; border-radius: 5px; }
            .user { background-color: #e3f2fd; text-align: right; }
            .bot { background-color: #f5f5f5; }
            #input-container { display: flex; }
            #message-input { flex: 1; padding: 10px; border: 1px solid #ddd; }
            #send-button { padding: 10px 20px; background-color: #007bff; color: white; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>3MTT Support Chat</h1>
        <div id="chat-container"></div>
        <div id="input-container">
            <input type="text" id="message-input" placeholder="Type your message..." onkeypress="handleKeyPress(event)">
            <button id="send-button" onclick="sendMessage()">Send</button>
        </div>

        <script>
            function addMessage(message, isUser) {
                const chatContainer = document.getElementById('chat-container');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + (isUser ? 'user' : 'bot');
                messageDiv.textContent = message;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
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
                .catch(error => addMessage('Sorry, something went wrong. Please try again.', false));
            }

            function handleKeyPress(event) {
                if (event.key === 'Enter') sendMessage();
            }

            // Add welcome message
            addMessage('Hello! Welcome to 3MTT support. How can I help you today?', false);
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Load conversation history for context
    try:
        with open('conversations.json', 'r') as f:
            conversation_history = json.load(f)
    except FileNotFoundError:
        conversation_history = []
    
    # Get AI response with context
    bot_response = get_ai_response(user_message, conversation_history)
    
    # Get or create session ID
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    # Save conversation with session tracking
    save_conversation(user_message, bot_response, session['session_id'])
    
    return jsonify({'response': bot_response})

@app.route('/admin/analytics')
def analytics():
    """Admin dashboard for conversation analytics"""
    try:
        with open('conversations.json', 'r') as f:
            conversations = json.load(f)
    except FileNotFoundError:
        conversations = []
    
    # Basic analytics
    total_conversations = len(conversations)
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    unique_sessions = set()
    
    for conv in conversations:
        sentiment_counts[conv.get("sentiment", "neutral")] += 1
        unique_sessions.add(conv.get("session_id", "anonymous"))
    
    analytics_html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>3MTT Chatbot Analytics</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
            .metric {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }}
            .metric h3 {{ margin: 0 0 10px 0; color: #333; }}
            .metric p {{ margin: 0; font-size: 24px; font-weight: bold; color: #007bff; }}
        </style>
    </head>
    <body>
        <h1>3MTT Chatbot Analytics</h1>
        
        <div class="metric">
            <h3>Total Conversations</h3>
            <p>{total_conversations}</p>
        </div>
        
        <div class="metric">
            <h3>Unique Sessions</h3>
            <p>{len(unique_sessions)}</p>
        </div>
        
        <div class="metric">
            <h3>Sentiment Distribution</h3>
            <p>Positive: {sentiment_counts['positive']} | Neutral: {sentiment_counts['neutral']} | Negative: {sentiment_counts['negative']}</p>
        </div>
        
        <div class="metric">
            <h3>Recent Conversations</h3>
            <div style="max-height: 300px; overflow-y: scroll; border: 1px solid #ddd; padding: 10px;">
                {"".join([f"<p><strong>User:</strong> {conv.get('user_message', '')[:100]}...</p><p><strong>Bot:</strong> {conv.get('bot_response', '')[:100]}...</p><hr>" for conv in conversations[-10:]])}
            </div>
        </div>
        
        <p><a href="/">← Back to Chat</a></p>
    </body>
    </html>
    '''
    return render_template_string(analytics_html)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
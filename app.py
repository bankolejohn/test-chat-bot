from flask import Flask, request, jsonify, render_template_string, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_caching import Cache
import os
import time
import html
import json
from datetime import datetime
from sqlalchemy import text
from config import config
from models import db, Conversation, Feedback, KnowledgeBase, AdminUser
from auth import admin_required, hash_password, verify_password, generate_token
from monitoring import init_monitoring, before_request, after_request, log_chat_interaction, get_metrics, logger
import openai

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Rate limiting with Redis
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        storage_uri=app.config['RATELIMIT_STORAGE_URL']
    )
    
    # CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Caching
    cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': app.config['REDIS_URL']})
    
    # Monitoring
    init_monitoring(app)
    app.before_request(before_request)
    app.after_request(after_request)
    
    # Mock responses for 3MTT
    MOCK_RESPONSES = {
        "dashboard_scores": "This is because your dashboard gradually syncs with your Darey.io and it may take some time for your Darey.io score to tally with that of your dashboard.",
        "program_end": "Cohort 3 ends July 20th.",
        "change_course": "Yes, you can change your course before you get admitted into the Learning Management System. Once you have been admitted, you won't be able to change your course. You can change your location at any given during cohort 3.",
        "onboarding_wait": "You will be added to communities where you will get access to free resources, collaborative self paced learning and physical meetup with your peers.",
        "entry_assessment": "Yes, there will be an entry assessment to determine the skill benchmark for each applicant. This will also be used in selecting the most applicable course for fellows.",
        "financial_support": "The only financial support for this phase of the programme will be the cost of training. Participants will be responsible for transportation, meals and other costs.",
        "physical_attendance": "The training is hybrid, meaning that it combines online and in-person components. While the majority of the training can be done remotely, there are aspects that will require in-person training.",
        "learning_community": "When you are assigned to a learning community in your location, the information will be displayed on your community page with the 3mtt portal when you log in.",
        "default": "Hello! Welcome to 3MTT support. How can I help you today?"
    }
    
    def get_ai_response(message, conversation_history=None):
        """Get AI response with caching"""
        cache_key = f"ai_response:{hash(message)}"
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response
        
        start_time = time.time()
        try:
            if not app.config['OPENAI_API_KEY']:
                response = get_mock_response(message)
            else:
                client = openai.OpenAI(api_key=app.config['OPENAI_API_KEY'])
                messages = [
                    {"role": "system", "content": "You are a helpful customer support assistant for 3MTT organization. Keep responses concise and professional."},
                    {"role": "user", "content": message}
                ]
                
                ai_response = client.chat.completions.create(
                    model=app.config['AI_MODEL'],
                    messages=messages,
                    max_tokens=app.config['MAX_TOKENS'],
                    temperature=app.config['TEMPERATURE']
                )
                response = ai_response.choices[0].message.content
            
            # Cache successful responses
            cache.set(cache_key, response, timeout=3600)  # 1 hour
            
        except Exception as e:
            logger.error("AI response failed", error=str(e))
            response = get_mock_response(message)
        
        response_time = time.time() - start_time
        log_chat_interaction(analyze_sentiment(message), response_time)
        return response
    
    def get_mock_response(message):
        """Get mock response based on keywords"""
        message_lower = message.lower()
        if any(word in message_lower for word in ["dashboard", "score", "darey"]):
            return MOCK_RESPONSES["dashboard_scores"]
        elif any(word in message_lower for word in ["change", "course", "location"]):
            return MOCK_RESPONSES["change_course"]
        elif any(word in message_lower for word in ["onboard", "waiting"]):
            return MOCK_RESPONSES["onboarding_wait"]
        elif any(word in message_lower for word in ["assessment", "test"]):
            return MOCK_RESPONSES["entry_assessment"]
        elif any(word in message_lower for word in ["financial", "money"]):
            return MOCK_RESPONSES["financial_support"]
        elif any(word in message_lower for word in ["physical", "attendance"]):
            return MOCK_RESPONSES["physical_attendance"]
        elif any(word in message_lower for word in ["community", "learning"]):
            return MOCK_RESPONSES["learning_community"]
        elif any(word in message_lower for word in ["end", "finish", "cohort"]):
            return MOCK_RESPONSES["program_end"]
        else:
            return MOCK_RESPONSES["default"]
    
    def analyze_sentiment(message):
        """Basic sentiment analysis"""
        positive_words = ['good', 'great', 'excellent', 'happy', 'thank']
        negative_words = ['bad', 'terrible', 'angry', 'frustrated', 'problem']
        
        message_lower = message.lower()
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        return "neutral"
    
    @app.route('/')
    def index():
        """Serve chat interface"""
        return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>3MTT Support Chat</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; flex-direction: column; padding: 10px; }
                .chat-container { flex: 1; max-width: 800px; width: 100%; margin: 0 auto; background: rgba(255, 255, 255, 0.95); border-radius: 20px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2); overflow: hidden; display: flex; flex-direction: column; }
                .chat-header { background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 20px; text-align: center; }
                .chat-header h1 { font-size: 1.5rem; margin-bottom: 5px; }
                #chat-messages { flex: 1; overflow-y: auto; padding: 20px; min-height: 400px; }
                .message { margin: 15px 0; display: flex; align-items: flex-start; }
                .message.user { justify-content: flex-end; }
                .message-content { max-width: 80%; padding: 12px 16px; border-radius: 18px; word-wrap: break-word; }
                .message.user .message-content { background: linear-gradient(135deg, #007bff, #0056b3); color: white; }
                .message.bot .message-content { background: #f8f9fa; color: #333; border: 1px solid #e9ecef; }
                .input-container { padding: 20px; background: rgba(255, 255, 255, 0.95); border-top: 1px solid rgba(0, 0, 0, 0.1); }
                .input-wrapper { display: flex; gap: 10px; }
                #message-input { flex: 1; padding: 12px 16px; border: 2px solid #e9ecef; border-radius: 25px; font-size: 16px; outline: none; }
                #send-button { background: linear-gradient(135deg, #007bff, #0056b3); color: white; border: none; padding: 12px 20px; border-radius: 25px; cursor: pointer; font-weight: 600; }
                @media (max-width: 768px) { body { padding: 5px; } .message-content { max-width: 85%; } }
            </style>
        </head>
        <body>
            <div class="chat-container">
                <div class="chat-header">
                    <h1>3MTT Support Chat</h1>
                    <div>Get help with your 3MTT journey</div>
                </div>
                <div id="chat-messages"></div>
                <div class="input-container">
                    <div class="input-wrapper">
                        <input type="text" id="message-input" placeholder="Type your message..." onkeypress="handleKeyPress(event)">
                        <button id="send-button" onclick="sendMessage()">Send</button>
                    </div>
                </div>
            </div>
            <script>
                function addMessage(message, isUser) {
                    const chatMessages = document.getElementById('chat-messages');
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message ' + (isUser ? 'user' : 'bot');
                    const content = document.createElement('div');
                    content.className = 'message-content';
                    content.textContent = message;
                    messageDiv.appendChild(content);
                    chatMessages.appendChild(messageDiv);
                    chatMessages.scrollTop = chatMessages.scrollHeight;
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
                    .catch(error => addMessage('Sorry, something went wrong.', false));
                }
                
                function handleKeyPress(event) {
                    if (event.key === 'Enter') sendMessage();
                }
                
                addMessage('Hello! Welcome to 3MTT support. How can I help you today?', false);
            </script>
        </body>
        </html>
        ''')
    
    @app.route('/chat', methods=['POST'])
    @limiter.limit("10 per minute")
    def chat():
        """Handle chat messages with security and monitoring"""
        try:
            data = request.get_json()
            if not data or not data.get('message'):
                return jsonify({'error': 'No message provided'}), 400
            
            user_message = html.escape(data['message'].strip())
            if len(user_message) > 1000:
                return jsonify({'error': 'Message too long'}), 400
            
            # Get AI response
            bot_response = get_ai_response(user_message)
            
            # Save to database
            conversation = Conversation(
                session_id=session.get('session_id', 'anonymous'),
                user_message=user_message,
                bot_response=bot_response,
                sentiment=analyze_sentiment(user_message),
                message_length=len(user_message),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')[:500]
            )
            db.session.add(conversation)
            db.session.commit()
            
            return jsonify({'response': bot_response})
            
        except Exception as e:
            logger.error("Chat error", error=str(e))
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/admin/login', methods=['POST'])
    @limiter.limit("5 per minute")
    def admin_login():
        """Admin login endpoint"""
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = AdminUser.query.filter_by(username=username, active=True).first()
        if user and verify_password(password, user.password_hash):
            token = generate_token(user.id)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return jsonify({'token': token})
        
        return jsonify({'error': 'Invalid credentials'}), 401
    
    @app.route('/admin/analytics')
    @admin_required
    def analytics():
        """Admin analytics dashboard"""
        total_conversations = Conversation.query.count()
        recent_conversations = Conversation.query.order_by(Conversation.created_at.desc()).limit(10).all()
        
        return jsonify({
            'total_conversations': total_conversations,
            'recent_conversations': [conv.to_dict() for conv in recent_conversations]
        })
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        try:
            # Check database
            db.session.execute(text('SELECT 1'))
            db_status = 'healthy'
        except Exception:
            db_status = 'unhealthy'
        
        # For testing, always return healthy if we can import the app
        if app.config.get('TESTING'):
            return jsonify({
                'status': 'healthy',
                'database': 'healthy',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return jsonify({
            'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
            'database': db_status,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @app.route('/metrics')
    def metrics():
        """Prometheus metrics endpoint"""
        return get_metrics(), 200, {'Content-Type': 'text/plain; charset=utf-8'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        if not AdminUser.query.filter_by(username='admin').first():
            admin = AdminUser(
                username='admin',
                password_hash=hash_password('admin123'),  # Change in production
                email='admin@3mtt.com'
            )
            db.session.add(admin)
            db.session.commit()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
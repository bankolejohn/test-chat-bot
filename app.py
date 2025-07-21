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

def load_knowledge_base():
    """Load knowledge base from JSON file"""
    try:
        with open('knowledge_base.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Knowledge base file not found. Using basic knowledge.")
        return {}

def flatten_dict_value(value, key_context=""):
    """Flatten dictionary values for better searching"""
    if isinstance(value, dict):
        result = []
        for k, v in value.items():
            if isinstance(v, str):
                result.append(f"{k}: {v}")
            elif isinstance(v, list):
                result.append(f"{k}: {', '.join(str(item) for item in v)}")
            else:
                result.append(f"{k}: {str(v)}")
        return "; ".join(result)
    elif isinstance(value, list):
        return ", ".join(str(item) for item in value)
    else:
        return str(value)

def search_knowledge_base(query, knowledge_base):
    """Search knowledge base for relevant information with better matching"""
    query_lower = query.lower()
    query_words = [word.strip() for word in query_lower.split() if len(word.strip()) > 2]
    
    # Define specific keyword mappings for better matching
    keyword_mappings = {
        'dashboard': ['dashboard', 'score', 'sync', 'darey', 'different'],
        'course': ['course', 'track', 'change', 'switch', 'program'],
        'assessment': ['assessment', 'test', 'exam', 'evaluation', 'entry'],
        'financial': ['financial', 'cost', 'fee', 'money', 'payment', 'support'],
        'timeline': ['end', 'finish', 'when', 'date', 'timeline', 'cohort'],
        'community': ['community', 'learning', 'group', 'assigned'],
        'support': ['support', 'help', 'contact', 'assistance', 'hours'],
        'onboarding': ['onboard', 'wait', 'waiting', 'start'],
        'platform': ['platform', 'portal', 'login', 'access']
    }
    
    # Score each section based on relevance
    section_scores = {}
    
    for section, content in knowledge_base.items():
        score = 0
        matched_content = []
        
        if isinstance(content, dict):
            for key, value in content.items():
                key_lower = key.lower()
                
                # Flatten complex values for better searching
                flattened_value = flatten_dict_value(value, key)
                value_str = flattened_value.lower()
                
                # Direct word matching
                for word in query_words:
                    if word in key_lower or word in value_str:
                        score += 2
                        content_key = f"{section}.{key}"
                        if content_key not in [item.split(': ')[0] for item in matched_content]:
                            # Use original value for display, not flattened
                            if isinstance(value, str):
                                matched_content.append(f"{content_key}: {value}")
                            else:
                                matched_content.append(f"{content_key}: {flattened_value}")
                
                # Keyword category matching
                for category, keywords in keyword_mappings.items():
                    if any(kw in query_lower for kw in keywords):
                        if any(kw in key_lower or kw in value_str for kw in keywords):
                            score += 3
                            content_key = f"{section}.{key}"
                            if content_key not in [item.split(': ')[0] for item in matched_content]:
                                if isinstance(value, str):
                                    matched_content.append(f"{content_key}: {value}")
                                else:
                                    matched_content.append(f"{content_key}: {flattened_value}")
        
        if score > 0:
            section_scores[section] = {'score': score, 'content': matched_content}
    
    # Return most relevant content
    if not section_scores:
        return []
    
    # Sort by score and return top matches
    sorted_sections = sorted(section_scores.items(), key=lambda x: x[1]['score'], reverse=True)
    relevant_info = []
    
    for section, data in sorted_sections[:2]:  # Top 2 sections
        relevant_info.extend(data['content'][:2])  # Top 2 items per section
    
    return relevant_info[:3]  # Maximum 3 items total

def get_ai_response(message, conversation_history=None):
    """Get response from OpenAI API with knowledge base context"""
    try:
        import openai
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("No OpenAI API key found. Using enhanced mock responses.")
            return get_enhanced_mock_response(message)
        
        client = openai.OpenAI(api_key=api_key)
        
        # Load knowledge base
        knowledge_base = load_knowledge_base()
        relevant_info = search_knowledge_base(message, knowledge_base)
        
        # Build enhanced system prompt with knowledge base
        knowledge_context = ""
        if relevant_info:
            # Extract clean information from search results
            clean_info = []
            for info in relevant_info:
                if ': ' in info:
                    clean_info.append(info.split(': ', 1)[1])
                else:
                    clean_info.append(info)
            knowledge_context = "\n".join(f"- {info}" for info in clean_info)
        
        system_content = f"""You are a friendly and knowledgeable customer support assistant for 3MTT (3 Million Technical Talent), Nigeria's flagship technical skills development program.

ABOUT 3MTT:
3MTT is part of Nigeria's Renewed Hope agenda, aimed at building the country's technical talent backbone to power the digital economy. The program has trained 30,000 fellows in Phase 1 (launched December 2023) and plans to train 270,000 more in Phase 2 across three cohorts.

{f"RELEVANT INFORMATION FOR THIS QUERY:{chr(10)}{knowledge_context}" if knowledge_context else ""}

INSTRUCTIONS:
- Be conversational, helpful, and empathetic
- Provide complete, coherent answers that make sense
- Use the context above to give accurate information
- If you don't have specific information, be honest about it
- Always aim to be helpful and guide users to solutions
- Keep responses natural and human-like, not robotic
- Don't just list facts - explain them in context"""

        messages = [{"role": "system", "content": system_content}]
        
        # Add recent conversation history for context
        if conversation_history:
            for conv in conversation_history[-5:]:  # Last 5 exchanges
                messages.append({"role": "user", "content": conv.get("user_message", "")})
                messages.append({"role": "assistant", "content": conv.get("bot_response", "")})
        
        messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model=os.getenv('AI_MODEL', 'gpt-4'),
            messages=messages,
            max_tokens=int(os.getenv('MAX_TOKENS', '300')),
            temperature=float(os.getenv('TEMPERATURE', '0.7'))
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI Error: {e}")
        return get_enhanced_mock_response(message)

def create_intelligent_response(message, knowledge_base):
    """Create intelligent, contextual responses based on user intent"""
    message_lower = message.lower()
    
    # Define response templates for different intents
    response_templates = {
        'program_overview': {
            'keywords': ['what is 3mtt', 'about 3mtt', 'tell me about', 'program overview', 'what is the program'],
            'response': lambda kb: f"{kb['3mtt_program']['overview']} The program is part of Nigeria's Renewed Hope agenda and aims to train technical talent across multiple phases. Phase 1 launched in December 2023 with 30,000 fellows, while Phase 2 will train 270,000 more technical talents."
        },
        'dashboard_issues': {
            'keywords': ['dashboard', 'score', 'sync', 'different', 'darey'],
            'response': lambda kb: f"Don't worry about dashboard score differences - this is completely normal! {kb['platform']['dashboard_sync']} The system automatically updates, so just give it some time to sync properly."
        },
        'course_changes': {
            'keywords': ['change course', 'switch course', 'course change', 'different course'],
            'response': lambda kb: f"Yes, you can change your course, but timing matters! {kb['courses']['course_change_policy']} Also, {kb['courses']['location_change_policy']} So you have flexibility with location throughout the program."
        },
        'program_timeline': {
            'keywords': ['when end', 'program end', 'cohort end', 'finish', 'timeline'],
            'response': lambda kb: f"Cohort 3 ends on July 20th, 2024. The overall program runs for 12 months with different phases, and we're currently in an active phase of the program."
        },
        'financial_support': {
            'keywords': ['financial', 'money', 'cost', 'fee', 'payment', 'support'],
            'response': lambda kb: f"Here's what's covered financially: {kb['support']['financial_support']} The program covers your training costs, which is the main expense, but you'll need to handle your own transportation and meals for in-person sessions."
        },
        'available_courses': {
            'keywords': ['what courses', 'available tracks', 'course options', 'tracks available'],
            'response': lambda kb: f"We offer {len(kb['courses']['available_tracks'])} exciting tracks: {', '.join(kb['courses']['available_tracks'])}. Each track is designed to meet industry demands and help you build relevant skills for the digital economy."
        },
        'contact_support': {
            'keywords': ['contact', 'support', 'help', 'assistance', 'reach out'],
            'response': lambda kb: f"You can reach our support team through multiple channels: {', '.join(kb['support']['contact_methods'])}. Our office hours are {kb['support']['office_hours']}, and we're here to help with any 3MTT related questions!"
        },
        'onboarding_wait': {
            'keywords': ['waiting', 'onboard', 'when start', 'access'],
            'response': lambda kb: f"While you're waiting for full onboarding, you're not left empty-handed! {kb['onboarding']['waiting_period']} This gives you a head start on learning and connecting with your peers."
        },
        'assessments': {
            'keywords': ['assessment', 'test', 'exam', 'evaluation'],
            'response': lambda kb: f"Yes, there will be assessments! {kb['assessments']['entry_assessment']['purpose']} and they happen {kb['assessments']['entry_assessment']['timing']}. Don't worry - they're designed to help place you in the right track for your skill level."
        },
        'technical_issues': {
            'keywords': ['login', 'access', 'error', 'problem', 'trouble', 'issue', 'bug'],
            'response': lambda kb: f"I understand you're having technical difficulties. For login and access issues, please ensure you have a stable internet connection and are using a modern web browser as required. If the problem persists, please contact our support team through {', '.join(kb['support']['contact_methods'])} during our office hours: {kb['support']['office_hours']}."
        },
        'learning_community': {
            'keywords': ['community', 'group', 'peers', 'meetup', 'assigned'],
            'response': lambda kb: f"Great question about learning communities! {kb['support']['learning_communities']} {kb['onboarding']['community_assignment']} This helps you connect with fellow learners in your area for collaboration and support."
        },
        'program_phases': {
            'keywords': ['phase 1', 'phase 2', 'phases', 'cohort', 'fellows'],
            'response': lambda kb: f"The 3MTT program has multiple phases: Phase 1 launched in December 2023 with {kb['3mtt_program']['phase_1']['fellows_count']} and included {kb['3mtt_program']['phase_1']['training_approach']}. Phase 2 will be even bigger, targeting {kb['3mtt_program']['phase_2']['target']} in {kb['3mtt_program']['phase_2']['structure']}."
        }
    }
    
    # Find the best matching intent
    best_match = None
    max_matches = 0
    
    for intent, config in response_templates.items():
        matches = sum(1 for keyword in config['keywords'] if keyword in message_lower)
        if matches > max_matches:
            max_matches = matches
            best_match = intent
    
    # Generate response based on best match
    if best_match and max_matches > 0:
        try:
            return response_templates[best_match]['response'](knowledge_base)
        except KeyError as e:
            print(f"Missing knowledge base key: {e}")
            return get_mock_response(message)
    
    # Fallback to original mock responses
    return get_mock_response(message)

def get_enhanced_mock_response(message):
    """Enhanced mock response with intelligent, contextual responses"""
    knowledge_base = load_knowledge_base()
    
    if knowledge_base:
        return create_intelligent_response(message, knowledge_base)
    else:
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
            let currentMessageId = null;
            let currentSessionId = null;
            let lastUserMessage = '';
            let lastBotResponse = '';

            function addMessage(message, isUser, messageData = null) {
                const chatContainer = document.getElementById('chat-container');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + (isUser ? 'user' : 'bot');
                
                if (isUser) {
                    messageDiv.textContent = message;
                    lastUserMessage = message;
                } else {
                    messageDiv.innerHTML = message + 
                        '<div style="margin-top: 10px;">' +
                        '<button onclick="sendFeedback(true)" style="background: #28a745; color: white; border: none; padding: 5px 10px; margin-right: 5px; cursor: pointer; border-radius: 3px;">👍 Helpful</button>' +
                        '<button onclick="sendFeedback(false)" style="background: #dc3545; color: white; border: none; padding: 5px 10px; cursor: pointer; border-radius: 3px;">👎 Not Helpful</button>' +
                        '</div>';
                    lastBotResponse = message;
                    if (messageData) {
                        currentMessageId = messageData.message_id;
                        currentSessionId = messageData.session_id;
                    }
                }
                
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }

            function sendFeedback(helpful) {
                if (!currentMessageId) return;
                
                fetch('/feedback', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: currentSessionId,
                        message_id: currentMessageId,
                        user_message: lastUserMessage,
                        bot_response: lastBotResponse,
                        helpful: helpful,
                        rating: helpful ? 5 : 2
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        addMessage('Thank you for your feedback! 🙏', false);
                    }
                });
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
                .then(data => addMessage(data.response, false, data))
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
    
    return jsonify({
        'response': bot_response,
        'session_id': session['session_id'],
        'message_id': str(uuid.uuid4())
    })

@app.route('/admin/knowledge', methods=['GET', 'POST'])
def manage_knowledge():
    """Admin interface for managing knowledge base"""
    if request.method == 'POST':
        # Update knowledge base
        new_knowledge = request.get_json()
        try:
            with open('knowledge_base.json', 'w') as f:
                json.dump(new_knowledge, f, indent=2)
            return jsonify({'success': True, 'message': 'Knowledge base updated successfully'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    
    # Load current knowledge base
    knowledge_base = load_knowledge_base()
    
    knowledge_html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>3MTT Knowledge Base Management</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 1000px; margin: 50px auto; padding: 20px; }}
            .section {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }}
            textarea {{ width: 100%; height: 400px; font-family: monospace; }}
            button {{ padding: 10px 20px; background-color: #007bff; color: white; border: none; cursor: pointer; margin: 5px; }}
            .nav {{ margin-bottom: 20px; }}
            .nav a {{ margin-right: 15px; text-decoration: none; color: #007bff; }}
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/">← Chat</a>
            <a href="/admin/analytics">Analytics</a>
            <a href="/admin/knowledge">Knowledge Base</a>
        </div>
        
        <h1>Knowledge Base Management</h1>
        
        <div class="section">
            <h3>Current Knowledge Base</h3>
            <textarea id="knowledge-editor">{json.dumps(knowledge_base, indent=2)}</textarea>
            <br>
            <button onclick="updateKnowledge()">Update Knowledge Base</button>
            <button onclick="testKnowledge()">Test Knowledge Search</button>
        </div>
        
        <div class="section">
            <h3>Test Knowledge Search</h3>
            <input type="text" id="test-query" placeholder="Enter test query..." style="width: 70%; padding: 10px;">
            <button onclick="searchTest()">Search</button>
            <div id="search-results" style="margin-top: 10px; padding: 10px; background: white; border: 1px solid #ddd;"></div>
        </div>

        <script>
            function updateKnowledge() {{
                const knowledge = document.getElementById('knowledge-editor').value;
                try {{
                    const parsed = JSON.parse(knowledge);
                    fetch('/admin/knowledge', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(parsed)
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        alert(data.message);
                        if (data.success) location.reload();
                    }});
                }} catch (e) {{
                    alert('Invalid JSON format: ' + e.message);
                }}
            }}
            
            function searchTest() {{
                const query = document.getElementById('test-query').value;
                fetch('/admin/test-search', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ query: query }})
                }})
                .then(response => response.json())
                .then(data => {{
                    document.getElementById('search-results').innerHTML = 
                        '<h4>Search Results:</h4>' + 
                        data.results.map(r => '<p>• ' + r + '</p>').join('');
                }});
            }}
        </script>
    </body>
    </html>
    '''
    return render_template_string(knowledge_html)

@app.route('/admin/test-search', methods=['POST'])
def test_search():
    """Test knowledge base search"""
    data = request.get_json()
    query = data.get('query', '')
    knowledge_base = load_knowledge_base()
    results = search_knowledge_base(query, knowledge_base)
    return jsonify({'results': results})

@app.route('/feedback', methods=['POST'])
def collect_feedback():
    """Collect user feedback on responses"""
    data = request.get_json()
    feedback = {
        "timestamp": datetime.now().isoformat(),
        "session_id": data.get('session_id'),
        "message_id": data.get('message_id'),
        "user_message": data.get('user_message'),
        "bot_response": data.get('bot_response'),
        "rating": data.get('rating'),  # 1-5 stars
        "feedback_text": data.get('feedback_text', ''),
        "helpful": data.get('helpful', True)
    }
    
    try:
        with open('training_data.json', 'r') as f:
            training_data = json.load(f)
    except FileNotFoundError:
        training_data = {"training_examples": [], "feedback_data": [], "improvement_suggestions": []}
    
    training_data["feedback_data"].append(feedback)
    
    with open('training_data.json', 'w') as f:
        json.dump(training_data, f, indent=2)
    
    return jsonify({'success': True, 'message': 'Feedback collected successfully'})

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
    app.run(debug=True, port=5001)
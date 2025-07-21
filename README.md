# 3MTT AI-Powered Support Chatbot

An intelligent Flask-based chatbot for 3MTT customer support with advanced AI capabilities.

## AI Features

- **OpenAI GPT-4 Integration** with enhanced context awareness
- **Conversation Memory** - Maintains context across chat sessions
- **Sentiment Analysis** - Tracks user satisfaction and mood
- **Session Management** - Unique session tracking for personalized experience
- **Analytics Dashboard** - Admin insights into conversation patterns
- **Intelligent Fallbacks** - Smart mock responses when AI is unavailable
- **Configurable AI Models** - Support for different OpenAI models

## Core Features

- Flask backend with `/chat` API endpoint
- Simple HTML/JavaScript frontend (no frameworks)
- Real-time conversation logging with metadata
- Built-in responses for common 3MTT intents
- Admin analytics at `/admin/analytics`

## Setup & Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key and other settings
```

3. Run the application:
```bash
python app.py
```

4. Access the application:
   - Chat Interface: `http://localhost:5000`
   - Analytics Dashboard: `http://localhost:5000/admin/analytics`

## Usage

- Type messages in the chat interface
- The bot will respond using OpenAI GPT-4 (if API key is set) or mock responses
- All conversations are saved to `conversations.json`

## Testing Examples

Try these sample questions to see AI capabilities:
- "Why is 3MTT dashboard scores different from Darey.io?"
- "When does the program end?"
- "I'm frustrated with the course selection process"
- "Can you help me understand the assessment requirements?"
- "Thank you for the helpful information!"

The AI will:
- Remember previous questions in your session
- Analyze sentiment (positive/negative/neutral)
- Provide contextual responses based on 3MTT knowledge
- Fall back to intelligent mock responses if needed
- Learn from user feedback to improve responses

## Training & Knowledge Base

### Knowledge Base Management
Access the knowledge base editor at `/admin/knowledge` to:
- View and edit the current knowledge base
- Test knowledge search functionality
- Add new information and topics

### Training the AI
1. **Automatic Learning**: The AI learns from user interactions and feedback
2. **Manual Training**: Run the training script to analyze performance:
   ```bash
   python train_chatbot.py
   ```
3. **Feedback Collection**: Users can rate responses with 👍/👎 buttons
4. **Analytics**: Monitor performance at `/admin/analytics`

### Adding Knowledge
To add new knowledge to your chatbot:

1. **Edit knowledge_base.json** directly or use the admin interface
2. **Add training examples** in training_data.json
3. **Structure your knowledge** in categories like:
   ```json
   {
     "new_topic": {
       "overview": "Description of the topic",
       "details": {
         "subtopic1": "Detailed information",
         "subtopic2": "More details"
       }
     }
   }
   ```

### Training Data Format
```json
{
  "training_examples": [
    {
      "user_input": "Sample question",
      "expected_response": "Ideal response",
      "category": "topic_category",
      "keywords": ["key", "words"]
    }
  ]
}
```

## Files

- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `conversations.json` - Chat history (created automatically)
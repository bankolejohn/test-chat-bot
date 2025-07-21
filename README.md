# 3MTT Support Chatbot

A minimal Flask-based chatbot for 3MTT customer support interactions.

## Features

- Flask backend with `/chat` API endpoint
- Simple HTML/JavaScript frontend (no frameworks)
- OpenAI GPT-4 integration with fallback mock responses
- Conversation logging to JSON file
- Built-in responses for common intents:
  - Dashboard score sync issues
  - Program end date
  - Contact support

## Setup & Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Set OpenAI API key:
```bash
export OPENAI_API_KEY=your_api_key_here
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and go to: `http://localhost:5000`

## Usage

- Type messages in the chat interface
- The bot will respond using OpenAI GPT-4 (if API key is set) or mock responses
- All conversations are saved to `conversations.json`

## Testing Examples

Try these sample questions:
- "Why is 3MTT dashboard scores different from Darey.io?"
- "When does the program end?"
- "When does cohort 3 finish?"
- "How can I contact support?"

## Files

- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `conversations.json` - Chat history (created automatically)
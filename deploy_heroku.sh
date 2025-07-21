#!/bin/bash
# Heroku Deployment Script

echo "🚀 Deploying 3MTT Chatbot to Heroku"

# Login to Heroku
heroku login

# Create new Heroku app
heroku create your-3mtt-chatbot

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key-here
heroku config:set OPENAI_API_KEY=your-openai-key-here

# Deploy
git add .
git commit -m "Deploy 3MTT chatbot"
git push heroku main

echo "✅ Deployment complete! Your chatbot is live at:"
heroku open
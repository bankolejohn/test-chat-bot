#!/bin/bash
set -e

echo "🚀 Deploying Simplified 3MTT Chatbot to Elastic Beanstalk"

# Use minimal requirements
cp requirements-minimal.txt requirements.txt

# Check if EB is initialized
if [ ! -f .elasticbeanstalk/config.yml ]; then
    echo "🔧 Initializing EB..."
    eb init 3mtt-chatbot-simple --platform python-3.11 --region us-east-1
fi

# Deploy
echo "📦 Deploying..."
eb deploy || eb create 3mtt-chatbot-simple-env --instance-type t3.micro

# Set environment variables
echo "⚙️ Setting environment variables..."
eb setenv OPENROUTER_API_KEY=$OPENROUTER_API_KEY SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(16))")

echo "✅ Deployment complete!"
eb open
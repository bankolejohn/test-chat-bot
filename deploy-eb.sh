#!/bin/bash
set -e

echo "🚀 Deploying 3MTT Chatbot to Elastic Beanstalk"

# Check prerequisites
command -v aws >/dev/null 2>&1 || { echo "❌ AWS CLI required"; exit 1; }
command -v eb >/dev/null 2>&1 || { echo "❌ EB CLI required. Install: pip install awsebcli"; exit 1; }

# Create deployment package
echo "📦 Creating deployment package..."
cp requirements-eb.txt requirements.txt

# Initialize EB application (if not exists)
if [ ! -f .elasticbeanstalk/config.yml ]; then
    echo "🔧 Initializing Elastic Beanstalk application..."
    eb init 3mtt-chatbot --platform python-3.11 --region us-east-1
fi

# Create environment (if not exists)
if ! eb status 2>/dev/null; then
    echo "🌍 Creating Elastic Beanstalk environment..."
    eb create 3mtt-chatbot-prod --instance-type t3.micro --envvars OPENROUTER_API_KEY=$OPENROUTER_API_KEY,SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
else
    echo "🔄 Deploying to existing environment..."
    eb deploy
fi

# Get application URL
echo "✅ Deployment complete!"
eb status | grep "CNAME"
echo "🌐 Your chatbot is live!"
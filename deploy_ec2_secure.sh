#!/bin/bash
# AWS EC2 Secure Deployment Script for 3MTT Chatbot

echo "🚀 Deploying 3MTT Chatbot to AWS EC2 (Secure Version)"
echo "=================================================="

# Function to generate random secret key
generate_secret_key() {
    python3 -c "import secrets; print(secrets.token_urlsafe(32))"
}

# Update system
echo "📦 Updating system packages..."
sudo yum update -y

# Install Python 3.11
echo "🐍 Installing Python 3.11..."
sudo yum install -y python3.11 python3.11-pip

# Install Git
echo "📥 Installing Git..."
sudo yum install -y git

# Clone repository
echo "📂 Cloning repository..."
if [ -z "$1" ]; then
    echo "❌ Error: Please provide your GitHub repository URL"
    echo "Usage: ./deploy_ec2_secure.sh https://github.com/username/3mtt-chatbot.git"
    exit 1
fi

REPO_URL=$1
git clone $REPO_URL
REPO_NAME=$(basename $REPO_URL .git)
cd $REPO_NAME

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip3.11 install -r requirements.txt

# Install Gunicorn
pip3.11 install gunicorn

# Create secure environment file
echo "🔐 Setting up environment variables..."
if [ ! -f .env ]; then
    echo "Creating .env file..."
    SECRET_KEY=$(generate_secret_key)
    cat > .env << EOF
# Flask Configuration
SECRET_KEY=$SECRET_KEY
FLASK_ENV=production

# OpenAI Configuration (optional - add your key here)
# OPENAI_API_KEY=sk-your-openai-key-here

# Application Settings
AI_MODEL=gpt-4
MAX_TOKENS=300
TEMPERATURE=0.7
EOF
    
    echo "✅ Generated secure SECRET_KEY automatically"
    echo "⚠️  To enable OpenAI features, edit .env and add your OPENAI_API_KEY"
    echo "   nano .env"
else
    echo "✅ .env file already exists"
fi

# Secure the environment file
chmod 600 .env
echo "🔒 Secured .env file permissions (600)"

# Install and configure Nginx
echo "🌐 Installing and configuring Nginx..."
sudo yum install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Create systemd service with secure environment loading
echo "⚙️  Creating systemd service..."
sudo tee /etc/systemd/system/3mtt-chatbot.service > /dev/null <<EOF
[Unit]
Description=3MTT Chatbot Flask App
After=network.target

[Service]
Type=simple
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/$REPO_NAME
EnvironmentFile=/home/ec2-user/$REPO_NAME/.env
ExecStart=/usr/local/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 --timeout 120 app:app
Restart=always
RestartSec=3

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/ec2-user/$REPO_NAME

[Install]
WantedBy=multi-user.target
EOF

# Start the service
echo "🚀 Starting the chatbot service..."
sudo systemctl daemon-reload
sudo systemctl start 3mtt-chatbot
sudo systemctl enable 3mtt-chatbot

# Check service status
if sudo systemctl is-active --quiet 3mtt-chatbot; then
    echo "✅ Chatbot service is running"
else
    echo "❌ Chatbot service failed to start. Check logs:"
    echo "   sudo journalctl -u 3mtt-chatbot -f"
    exit 1
fi

# Configure Nginx with security headers
echo "🔧 Configuring Nginx with security headers..."
sudo tee /etc/nginx/conf.d/3mtt-chatbot.conf > /dev/null <<EOF
server {
    listen 80;
    server_name _;  # Replace with your domain

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=chatbot:10m rate=10r/m;
    limit_req zone=chatbot burst=20 nodelay;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Test Nginx configuration
if sudo nginx -t; then
    echo "✅ Nginx configuration is valid"
    sudo systemctl restart nginx
else
    echo "❌ Nginx configuration error"
    exit 1
fi

# Setup log rotation
echo "📝 Setting up log rotation..."
sudo tee /etc/logrotate.d/3mtt-chatbot > /dev/null <<EOF
/home/ec2-user/$REPO_NAME/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 ec2-user ec2-user
}
EOF

# Create update script
echo "🔄 Creating update script..."
cat > update_chatbot.sh << 'EOF'
#!/bin/bash
echo "🔄 Updating 3MTT Chatbot..."
git pull origin main
pip3.11 install -r requirements.txt
sudo systemctl restart 3mtt-chatbot
echo "✅ Update complete!"
EOF
chmod +x update_chatbot.sh

# Final security check
echo "🔐 Final security check..."
ls -la .env
echo "Environment file permissions: $(stat -c %a .env)"

# Get instance public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo "✅ Your 3MTT Chatbot is now running securely on AWS EC2"
echo "🌐 Access your chatbot at: http://$PUBLIC_IP"
echo "📊 Admin analytics: http://$PUBLIC_IP/admin/analytics"
echo "🔧 Knowledge base: http://$PUBLIC_IP/admin/knowledge"
echo ""
echo "🔒 Security Features Enabled:"
echo "   • Environment variables stored securely in .env"
echo "   • Service runs with restricted permissions"
echo "   • Nginx security headers configured"
echo "   • Rate limiting enabled"
echo "   • Log rotation configured"
echo ""
echo "📝 Important Files:"
echo "   • Environment: /home/ec2-user/$REPO_NAME/.env"
echo "   • Service logs: sudo journalctl -u 3mtt-chatbot -f"
echo "   • Nginx logs: sudo tail -f /var/log/nginx/access.log"
echo "   • Update script: ./update_chatbot.sh"
echo ""
echo "⚠️  Next Steps:"
echo "   1. Edit .env file to add your OPENAI_API_KEY if needed"
echo "   2. Configure your domain name in Nginx config"
echo "   3. Set up SSL certificate (Let's Encrypt recommended)"
echo "   4. Configure AWS Security Groups for your needs"
echo ""
echo "🔧 Useful Commands:"
echo "   • Restart service: sudo systemctl restart 3mtt-chatbot"
echo "   • Check status: sudo systemctl status 3mtt-chatbot"
echo "   • View logs: sudo journalctl -u 3mtt-chatbot -f"
echo "   • Update app: ./update_chatbot.sh"
EOF
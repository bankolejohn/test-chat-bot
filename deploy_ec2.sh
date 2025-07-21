#!/bin/bash
# AWS EC2 Deployment Script

echo "🚀 Deploying 3MTT Chatbot to AWS EC2"

# Update system
sudo yum update -y

# Install Python 3.11
sudo yum install -y python3.11 python3.11-pip

# Install Git
sudo yum install -y git

# Clone your repository
git clone https://github.com/your-username/3mtt-chatbot.git
cd 3mtt-chatbot

# Install dependencies
pip3.11 install -r requirements.txt

# Set environment variables
export SECRET_KEY="your-secret-key-here"
export OPENAI_API_KEY="your-openai-key-here"

# Install and configure Nginx
sudo yum install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Install Gunicorn
pip3.11 install gunicorn

# Create systemd service
sudo tee /etc/systemd/system/3mtt-chatbot.service > /dev/null <<EOF
[Unit]
Description=3MTT Chatbot Flask App
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/3mtt-chatbot
Environment=SECRET_KEY=your-secret-key-here
Environment=OPENAI_API_KEY=your-openai-key-here
ExecStart=/usr/local/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start the service
sudo systemctl daemon-reload
sudo systemctl start 3mtt-chatbot
sudo systemctl enable 3mtt-chatbot

# Configure Nginx
sudo tee /etc/nginx/conf.d/3mtt-chatbot.conf > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Restart Nginx
sudo systemctl restart nginx

echo "✅ Deployment complete! Your chatbot is running on port 80"
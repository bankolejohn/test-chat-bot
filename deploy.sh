#!/bin/bash
# EC2 deployment script

# Update system
sudo apt update
sudo apt install -y python3-pip python3-venv nginx

# Setup application
cd /home/ubuntu/test-chatbot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Kill existing process
sudo pkill -f "python3 app.py" || true

# Start application
nohup python3 app.py > app.log 2>&1 &

# Setup nginx reverse proxy
sudo tee /etc/nginx/sites-available/chatbot > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

echo "Deployment complete - App running on port 80"
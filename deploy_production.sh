#!/bin/bash
# Production Deployment Script for 3MTT Chatbot

set -e  # Exit on any error

echo "🚀 3MTT Chatbot Production Deployment"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Don't run this script as root for security reasons"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
required_version="3.11"
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    print_error "Python 3.11+ required. Current version: $python_version"
    exit 1
fi
print_status "Python version check passed: $python_version"

# Create production directories
print_status "Creating production directories..."
mkdir -p logs
mkdir -p backups
mkdir -p data

# Backup existing data
if [ -f "conversations.json" ]; then
    cp conversations.json "backups/conversations_$(date +%Y%m%d_%H%M%S).json"
    print_status "Backed up existing conversations"
fi

# Install production dependencies
print_status "Installing production dependencies..."
pip3 install -r requirements.txt

# Run tests
print_status "Running production readiness tests..."
python3 run_tests.py
if [ $? -ne 0 ]; then
    print_error "Tests failed. Fix issues before deploying to production."
    exit 1
fi

# Check environment configuration
if [ ! -f ".env" ]; then
    print_warning "No .env file found. Creating from template..."
    cp .env.production .env
    print_warning "Please edit .env file with your production values before starting the app"
fi

# Validate environment file
if grep -q "CHANGE-THIS" .env; then
    print_error "Please update the SECRET_KEY in .env file before production deployment"
    exit 1
fi

# Set secure file permissions
chmod 600 .env
chmod 644 knowledge_base.json
chmod 755 *.py
print_status "Set secure file permissions"

# Create systemd service file (if on Linux)
if command -v systemctl &> /dev/null; then
    print_status "Creating systemd service..."
    
    cat > 3mtt-chatbot.service << EOF
[Unit]
Description=3MTT Chatbot Flask App
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$(pwd)
EnvironmentFile=$(pwd)/.env
ExecStart=$(which gunicorn) --workers 3 --bind 0.0.0.0:8000 --timeout 120 app:app
Restart=always
RestartSec=3

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$(pwd)

[Install]
WantedBy=multi-user.target
EOF

    print_status "Systemd service file created: 3mtt-chatbot.service"
    print_warning "To install: sudo cp 3mtt-chatbot.service /etc/systemd/system/"
    print_warning "To enable: sudo systemctl enable 3mtt-chatbot"
    print_warning "To start: sudo systemctl start 3mtt-chatbot"
fi

# Create nginx configuration (if nginx is available)
if command -v nginx &> /dev/null; then
    print_status "Creating nginx configuration..."
    
    cat > nginx-3mtt-chatbot.conf << EOF
server {
    listen 80;
    server_name your-domain.com;  # Change this to your domain

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=chatbot:10m rate=10r/m;
    limit_req zone=chatbot burst=20 nodelay;

    location / {
        proxy_pass http://127.0.0.1:8000;
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
        proxy_pass http://127.0.0.1:8000/health;
    }
}
EOF

    print_status "Nginx configuration created: nginx-3mtt-chatbot.conf"
    print_warning "To install: sudo cp nginx-3mtt-chatbot.conf /etc/nginx/sites-available/"
    print_warning "To enable: sudo ln -s /etc/nginx/sites-available/nginx-3mtt-chatbot.conf /etc/nginx/sites-enabled/"
    print_warning "To reload: sudo nginx -t && sudo systemctl reload nginx"
fi

# Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
# Simple monitoring script for 3MTT Chatbot

check_health() {
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
    if [ "$response" = "200" ]; then
        echo "$(date): Health check PASSED"
        return 0
    else
        echo "$(date): Health check FAILED (HTTP $response)"
        return 1
    fi
}

# Run health check
if check_health; then
    exit 0
else
    # Try to restart service if health check fails
    echo "$(date): Attempting to restart service..."
    sudo systemctl restart 3mtt-chatbot
    sleep 10
    
    if check_health; then
        echo "$(date): Service restarted successfully"
        exit 0
    else
        echo "$(date): Service restart failed - manual intervention required"
        exit 1
    fi
fi
EOF

chmod +x monitor.sh
print_status "Created monitoring script: monitor.sh"

# Create log rotation configuration
cat > logrotate-3mtt-chatbot << EOF
$(pwd)/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
    postrotate
        sudo systemctl reload 3mtt-chatbot
    endscript
}
EOF

print_status "Created log rotation config: logrotate-3mtt-chatbot"
print_warning "To install: sudo cp logrotate-3mtt-chatbot /etc/logrotate.d/"

# Final summary
echo ""
echo "🎉 Production Deployment Setup Complete!"
echo "========================================"
echo ""
echo "📋 Next Steps:"
echo "1. Review and update .env file with production values"
echo "2. Install systemd service: sudo cp 3mtt-chatbot.service /etc/systemd/system/"
echo "3. Install nginx config: sudo cp nginx-3mtt-chatbot.conf /etc/nginx/sites-available/"
echo "4. Start services: sudo systemctl start 3mtt-chatbot"
echo "5. Set up SSL certificate (recommended: Let's Encrypt)"
echo "6. Configure monitoring: Add monitor.sh to crontab"
echo ""
echo "🔍 Health Check: curl http://localhost:8000/health"
echo "📊 Admin Panel: http://your-domain.com/admin/analytics"
echo "💬 Chat Interface: http://your-domain.com/"
echo ""
echo "📝 Important Files:"
echo "   - Application: $(pwd)/app.py"
echo "   - Configuration: $(pwd)/.env"
echo "   - Logs: $(pwd)/logs/"
echo "   - Backups: $(pwd)/backups/"
echo ""
print_status "Your 3MTT Chatbot is ready for production! 🚀"
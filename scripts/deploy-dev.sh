#!/bin/bash
# Development Environment Deployment Script

set -e

echo "🚀 Deploying 3MTT Chatbot to Development Environment"
echo "=================================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Configuration
ENVIRONMENT="dev"
COMPOSE_FILE="environments/dev/docker-compose.dev.yml"
ENV_FILE="environments/dev/.env.dev"

# Pre-deployment checks
print_status "Running pre-deployment checks..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if environment file exists
if [ ! -f "$ENV_FILE" ]; then
    print_error "Environment file $ENV_FILE not found!"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Pre-deployment checks passed"

# Stop existing containers
print_status "Stopping existing development containers..."
docker-compose -f $COMPOSE_FILE down --remove-orphans || true

# Build and start services
print_status "Building and starting development services..."
docker-compose -f $COMPOSE_FILE up --build -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Health check
print_status "Running health checks..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    print_status "Health check passed!"
else
    print_error "Health check failed!"
    print_warning "Checking logs..."
    docker-compose -f $COMPOSE_FILE logs chatbot-dev
    exit 1
fi

# Run tests
print_status "Running development tests..."
docker-compose -f $COMPOSE_FILE exec -T chatbot-dev python -m pytest tests/ -v || {
    print_warning "Some tests failed, but continuing with development deployment"
}

# Display deployment information
echo ""
echo "🎉 Development Deployment Complete!"
echo "=================================="
echo ""
echo "📋 Service URLs:"
echo "   🤖 Chatbot:     http://localhost:5000"
echo "   📊 Admin:       http://localhost:5000/admin/analytics"
echo "   🗄️  Database:    http://localhost:8080 (Adminer)"
echo "   📈 Monitoring:  http://localhost:9090 (Prometheus)"
echo ""
echo "🔧 Useful Commands:"
echo "   View logs:      docker-compose -f $COMPOSE_FILE logs -f"
echo "   Stop services:  docker-compose -f $COMPOSE_FILE down"
echo "   Restart:        docker-compose -f $COMPOSE_FILE restart"
echo "   Shell access:   docker-compose -f $COMPOSE_FILE exec chatbot-dev bash"
echo ""
echo "📝 Development Notes:"
echo "   - Code changes will auto-reload"
echo "   - Debug mode is enabled"
echo "   - Verbose logging is active"
echo "   - Mock responses are used if no OpenAI key"
echo ""
print_status "Happy coding! 🚀"
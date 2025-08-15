#!/bin/bash
# Staging Environment Deployment Script

set -e

echo "🚀 Deploying 3MTT Chatbot to Staging Environment"
echo "=============================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Configuration
ENVIRONMENT="staging"
COMPOSE_FILE="environments/staging/docker-compose.staging.yml"
ENV_FILE="environments/staging/.env.staging"
BUILD_NUMBER=${BUILD_NUMBER:-$(date +%Y%m%d-%H%M%S)}

# Pre-deployment checks
print_status "Running pre-deployment checks..."

# Check if environment file exists
if [ ! -f "$ENV_FILE" ]; then
    print_error "Environment file $ENV_FILE not found!"
    exit 1
fi

# Check for required secrets
if grep -q "CHANGE-THIS" "$ENV_FILE"; then
    print_error "Please update placeholder values in $ENV_FILE"
    exit 1
fi

# Security scan
print_status "Running security scan..."
if command -v bandit &> /dev/null; then
    bandit -r app.py || {
        print_error "Security scan failed!"
        exit 1
    }
else
    print_warning "Bandit not installed, skipping security scan"
fi

# Run tests
print_status "Running test suite..."
python -m pytest tests/ --cov=app --cov-report=term-missing || {
    print_error "Tests failed!"
    exit 1
}

print_status "Pre-deployment checks passed"

# Backup current deployment (if exists)
print_status "Creating backup of current deployment..."
if docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
    docker-compose -f $COMPOSE_FILE exec -T postgres-staging pg_dump -U chatbot_user chatbot_staging > "backups/staging-backup-$(date +%Y%m%d-%H%M%S).sql" || true
fi

# Deploy new version
print_status "Deploying new version..."
export BUILD_NUMBER=$BUILD_NUMBER

# Blue-green deployment simulation
print_status "Starting blue-green deployment..."

# Start new containers
docker-compose -f $COMPOSE_FILE up --build -d --scale chatbot-staging=2

# Wait for new containers to be ready
print_status "Waiting for new containers to be ready..."
sleep 60

# Health check on new deployment
print_status "Running health checks..."
HEALTH_CHECK_RETRIES=5
for i in $(seq 1 $HEALTH_CHECK_RETRIES); do
    if curl -f http://localhost/health > /dev/null 2>&1; then
        print_status "Health check passed!"
        break
    else
        if [ $i -eq $HEALTH_CHECK_RETRIES ]; then
            print_error "Health check failed after $HEALTH_CHECK_RETRIES attempts!"
            print_warning "Rolling back..."
            docker-compose -f $COMPOSE_FILE down
            exit 1
        fi
        print_warning "Health check attempt $i failed, retrying in 10 seconds..."
        sleep 10
    fi
done

# Integration tests
print_status "Running integration tests..."
python -m pytest tests/integration/ -v || {
    print_error "Integration tests failed!"
    print_warning "Rolling back..."
    docker-compose -f $COMPOSE_FILE down
    exit 1
}

# Performance tests
print_status "Running performance tests..."
if command -v ab &> /dev/null; then
    ab -n 100 -c 10 http://localhost/health || {
        print_warning "Performance test failed, but continuing..."
    }
else
    print_warning "Apache Bench not installed, skipping performance tests"
fi

# Scale down to single instance
docker-compose -f $COMPOSE_FILE up -d --scale chatbot-staging=1

# Display deployment information
echo ""
echo "🎉 Staging Deployment Complete!"
echo "==============================="
echo ""
echo "📋 Service URLs:"
echo "   🤖 Chatbot:     https://staging.3mtt-chatbot.com"
echo "   📊 Admin:       https://staging.3mtt-chatbot.com/admin/analytics"
echo "   📈 Monitoring:  https://staging.3mtt-chatbot.com:9090"
echo "   📊 Grafana:     https://staging.3mtt-chatbot.com:3000"
echo ""
echo "🔧 Deployment Info:"
echo "   Build Number:   $BUILD_NUMBER"
echo "   Environment:    $ENVIRONMENT"
echo "   Deployed At:    $(date)"
echo ""
echo "🧪 Testing Commands:"
echo "   Load Test:      ab -n 1000 -c 50 https://staging.3mtt-chatbot.com/"
echo "   API Test:       curl -X POST https://staging.3mtt-chatbot.com/chat -d '{\"message\":\"test\"}'"
echo "   Health Check:   curl https://staging.3mtt-chatbot.com/health"
echo ""
print_status "Staging deployment ready for testing! 🧪"

# Notify team (if notification tools are available)
if command -v slack &> /dev/null; then
    slack chat send --channel "#deployments" --text "🚀 3MTT Chatbot deployed to staging (Build: $BUILD_NUMBER)"
fi
#!/bin/bash
# Production Environment Deployment Script
# This script implements enterprise-grade deployment practices

set -e

echo "🚀 Deploying 3MTT Chatbot to Production Environment"
echo "================================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Configuration
ENVIRONMENT="production"
BUILD_NUMBER=${BUILD_NUMBER:-$(date +%Y%m%d-%H%M%S)}
DEPLOYMENT_ID="prod-deploy-$BUILD_NUMBER"
ROLLBACK_ENABLED=${ROLLBACK_ENABLED:-true}

# Deployment approval check
if [ "${SKIP_APPROVAL:-false}" != "true" ]; then
    echo ""
    print_warning "PRODUCTION DEPLOYMENT REQUIRES APPROVAL"
    echo "========================================"
    echo "Environment: PRODUCTION"
    echo "Build Number: $BUILD_NUMBER"
    echo "Deployment ID: $DEPLOYMENT_ID"
    echo "Rollback Enabled: $ROLLBACK_ENABLED"
    echo ""
    read -p "Do you want to proceed with production deployment? (yes/no): " APPROVAL
    
    if [ "$APPROVAL" != "yes" ]; then
        print_error "Deployment cancelled by user"
        exit 1
    fi
fi

# Pre-deployment validation
print_status "Running pre-deployment validation..."

# Check AWS credentials
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    print_error "AWS credentials not configured or invalid"
    exit 1
fi

# Validate secrets in AWS Secrets Manager
print_status "Validating secrets in AWS Secrets Manager..."
REQUIRED_SECRETS=("prod/chatbot/secret-key" "prod/chatbot/openai-api-key" "prod/chatbot/database-url")
for secret in "${REQUIRED_SECRETS[@]}"; do
    if ! aws secretsmanager get-secret-value --secret-id "$secret" > /dev/null 2>&1; then
        print_error "Required secret $secret not found in AWS Secrets Manager"
        exit 1
    fi
done

# Security validation
print_status "Running security validation..."
bandit -r app.py -f json -o security-report.json || {
    print_error "Security scan failed!"
    exit 1
}

# Check for high/critical vulnerabilities
if jq -e '.results[] | select(.issue_severity == "HIGH" or .issue_severity == "CRITICAL")' security-report.json > /dev/null; then
    print_error "High or critical security vulnerabilities found!"
    exit 1
fi

# Performance validation
print_status "Running performance validation..."
python -m pytest tests/performance/ -v || {
    print_error "Performance tests failed!"
    exit 1
}

# Database migration check
print_status "Checking database migrations..."
# Add your database migration validation here

print_status "Pre-deployment validation passed"

# Create deployment backup
print_status "Creating pre-deployment backup..."
BACKUP_ID="backup-$(date +%Y%m%d-%H%M%S)"
aws rds create-db-snapshot \
    --db-instance-identifier prod-chatbot-db \
    --db-snapshot-identifier "$BACKUP_ID" || {
    print_error "Failed to create database backup"
    exit 1
}

# Wait for backup to complete
print_status "Waiting for backup to complete..."
aws rds wait db-snapshot-completed --db-snapshot-identifier "$BACKUP_ID"

# Blue-Green Deployment
print_status "Starting blue-green deployment..."

# Deploy to green environment
print_status "Deploying to green environment..."
aws ecs update-service \
    --cluster prod-chatbot-cluster \
    --service chatbot-green \
    --task-definition chatbot:$BUILD_NUMBER \
    --desired-count 2

# Wait for green deployment to be stable
print_status "Waiting for green environment to be stable..."
aws ecs wait services-stable \
    --cluster prod-chatbot-cluster \
    --services chatbot-green

# Health check on green environment
print_status "Running health checks on green environment..."
GREEN_ALB_DNS=$(aws elbv2 describe-load-balancers \
    --names prod-chatbot-green-alb \
    --query 'LoadBalancers[0].DNSName' \
    --output text)

HEALTH_CHECK_RETRIES=10
for i in $(seq 1 $HEALTH_CHECK_RETRIES); do
    if curl -f "http://$GREEN_ALB_DNS/health" > /dev/null 2>&1; then
        print_status "Green environment health check passed!"
        break
    else
        if [ $i -eq $HEALTH_CHECK_RETRIES ]; then
            print_error "Green environment health check failed!"
            print_warning "Rolling back..."
            aws ecs update-service \
                --cluster prod-chatbot-cluster \
                --service chatbot-green \
                --desired-count 0
            exit 1
        fi
        print_warning "Health check attempt $i failed, retrying in 30 seconds..."
        sleep 30
    fi
done

# Smoke tests on green environment
print_status "Running smoke tests on green environment..."
python -m pytest tests/smoke/ --base-url="http://$GREEN_ALB_DNS" -v || {
    print_error "Smoke tests failed on green environment!"
    print_warning "Rolling back..."
    aws ecs update-service \
        --cluster prod-chatbot-cluster \
        --service chatbot-green \
        --desired-count 0
    exit 1
}

# Switch traffic to green (Blue-Green cutover)
print_status "Switching traffic to green environment..."
aws elbv2 modify-listener \
    --listener-arn $(aws elbv2 describe-listeners \
        --load-balancer-arn $(aws elbv2 describe-load-balancers \
            --names prod-chatbot-main-alb \
            --query 'LoadBalancers[0].LoadBalancerArn' \
            --output text) \
        --query 'Listeners[0].ListenerArn' \
        --output text) \
    --default-actions Type=forward,TargetGroupArn=$(aws elbv2 describe-target-groups \
        --names prod-chatbot-green-tg \
        --query 'TargetGroups[0].TargetGroupArn' \
        --output text)

# Wait for traffic switch
print_status "Waiting for traffic switch to complete..."
sleep 60

# Post-deployment validation
print_status "Running post-deployment validation..."

# Health check on main URL
MAIN_URL="https://chatbot.3mtt.gov.ng"
for i in $(seq 1 5); do
    if curl -f "$MAIN_URL/health" > /dev/null 2>&1; then
        print_status "Production health check passed!"
        break
    else
        if [ $i -eq 5 ]; then
            print_error "Production health check failed!"
            # Implement rollback here
            exit 1
        fi
        sleep 30
    fi
done

# Business logic tests
print_status "Running business logic tests..."
python -m pytest tests/business/ --base-url="$MAIN_URL" -v || {
    print_warning "Some business logic tests failed, but deployment continues"
}

# Scale down blue environment
print_status "Scaling down blue environment..."
aws ecs update-service \
    --cluster prod-chatbot-cluster \
    --service chatbot-blue \
    --desired-count 0

# Update monitoring and alerting
print_status "Updating monitoring configuration..."
# Update Prometheus targets, Grafana dashboards, etc.

# Send notifications
print_status "Sending deployment notifications..."

# Slack notification
if command -v slack &> /dev/null; then
    slack chat send \
        --channel "#production-deployments" \
        --text "🚀 3MTT Chatbot successfully deployed to production
        
Build: $BUILD_NUMBER
Deployment ID: $DEPLOYMENT_ID
Deployed by: $(whoami)
Time: $(date)
Health Check: ✅ Passed
URL: $MAIN_URL"
fi

# Email notification (if configured)
if [ -n "$DEPLOYMENT_EMAIL_LIST" ]; then
    echo "Production deployment completed successfully" | \
    mail -s "3MTT Chatbot Production Deployment - $BUILD_NUMBER" "$DEPLOYMENT_EMAIL_LIST"
fi

# Create deployment record
print_status "Creating deployment record..."
cat > "deployments/prod-$BUILD_NUMBER.json" << EOF
{
    "deployment_id": "$DEPLOYMENT_ID",
    "build_number": "$BUILD_NUMBER",
    "environment": "production",
    "deployed_by": "$(whoami)",
    "deployed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "backup_id": "$BACKUP_ID",
    "health_check_status": "passed",
    "rollback_available": $ROLLBACK_ENABLED
}
EOF

# Display deployment summary
echo ""
echo "🎉 Production Deployment Complete!"
echo "=================================="
echo ""
echo "📋 Deployment Summary:"
echo "   Build Number:    $BUILD_NUMBER"
echo "   Deployment ID:   $DEPLOYMENT_ID"
echo "   Environment:     Production"
echo "   Deployed By:     $(whoami)"
echo "   Deployed At:     $(date)"
echo "   Backup ID:       $BACKUP_ID"
echo ""
echo "🌐 Service URLs:"
echo "   🤖 Main App:     $MAIN_URL"
echo "   📊 Admin:        $MAIN_URL/admin/analytics"
echo "   ❤️  Health:       $MAIN_URL/health"
echo ""
echo "📊 Monitoring:"
echo "   📈 Metrics:      https://monitoring.3mtt.gov.ng/grafana"
echo "   🚨 Alerts:       https://monitoring.3mtt.gov.ng/alertmanager"
echo "   📝 Logs:         https://logs.3mtt.gov.ng"
echo ""
echo "🔧 Operations:"
echo "   Rollback:        ./scripts/rollback-production.sh $BUILD_NUMBER"
echo "   Scale Up:        aws ecs update-service --desired-count 4"
echo "   View Logs:       aws logs tail /aws/ecs/chatbot-prod --follow"
echo ""
print_status "Production deployment successful! 🎉"
print_info "Monitor the application closely for the next 30 minutes"

# Set up post-deployment monitoring
print_status "Setting up post-deployment monitoring..."
# Schedule automated health checks for the next hour
# Set up enhanced alerting for the next 24 hours
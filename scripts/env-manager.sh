#!/bin/bash
# Environment Manager Script for 3MTT Chatbot
# Usage: ./scripts/env-manager.sh [command] [environment]

set -e

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

# Help function
show_help() {
    echo "🚀 3MTT Chatbot Environment Manager"
    echo "=================================="
    echo ""
    echo "Usage: $0 [command] [environment]"
    echo ""
    echo "Commands:"
    echo "  setup     - Set up environment configuration"
    echo "  deploy    - Deploy to specified environment"
    echo "  status    - Check environment status"
    echo "  logs      - View environment logs"
    echo "  test      - Run tests against environment"
    echo "  rollback  - Rollback to previous version"
    echo "  switch    - Switch your local environment"
    echo ""
    echo "Environments:"
    echo "  dev       - Development environment"
    echo "  staging   - Staging environment"
    echo "  prod      - Production environment"
    echo ""
    echo "Examples:"
    echo "  $0 setup dev"
    echo "  $0 deploy staging"
    echo "  $0 status prod"
    echo "  $0 logs dev"
    echo "  $0 test staging"
    echo ""
}

# Environment URLs
get_env_url() {
    case $1 in
        "dev")
            echo "http://localhost:5000"
            ;;
        "staging")
            echo "https://staging.3mtt-chatbot.com"
            ;;
        "prod")
            echo "https://chatbot.3mtt.gov.ng"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Setup environment
setup_environment() {
    local env=$1
    print_info "Setting up $env environment..."
    
    case $env in
        "dev")
            # Copy dev environment template
            if [ ! -f ".env" ]; then
                cp environments/dev/.env.dev .env
                print_status "Created .env file from dev template"
                print_warning "Please edit .env file with your local settings:"
                print_warning "  - Add your OPENAI_API_KEY"
                print_warning "  - Update SECRET_KEY if needed"
            else
                print_warning ".env file already exists"
            fi
            
            # Create necessary directories
            mkdir -p logs backups data
            
            # Install dependencies
            if [ -f "requirements.txt" ]; then
                print_info "Installing dependencies..."
                pip install -r requirements.txt
                print_status "Dependencies installed"
            fi
            ;;
            
        "staging")
            print_info "Staging environment is managed by CI/CD"
            print_info "Environment variables are set in GitHub Actions"
            print_info "To deploy to staging: git push origin develop"
            ;;
            
        "prod")
            print_info "Production environment is managed by AWS"
            print_info "Secrets are stored in AWS Secrets Manager"
            print_info "To deploy to production: create a release tag"
            ;;
    esac
}

# Deploy to environment
deploy_environment() {
    local env=$1
    print_info "Deploying to $env environment..."
    
    case $env in
        "dev")
            if [ -f "scripts/deploy-dev.sh" ]; then
                chmod +x scripts/deploy-dev.sh
                ./scripts/deploy-dev.sh
            else
                print_error "Development deployment script not found"
                exit 1
            fi
            ;;
            
        "staging")
            print_info "To deploy to staging:"
            print_info "1. Ensure your changes are in a feature branch"
            print_info "2. Create PR to develop branch"
            print_info "3. After approval, merge will trigger staging deployment"
            print_info ""
            print_info "Or push directly to develop (if you have permissions):"
            echo "   git checkout develop"
            echo "   git merge your-feature-branch"
            echo "   git push origin develop"
            ;;
            
        "prod")
            print_info "To deploy to production:"
            print_info "1. Ensure staging tests pass"
            print_info "2. Create PR from develop to main"
            print_info "3. After approval, create release tag:"
            echo "   git checkout main"
            echo "   git tag -a v1.x.x -m 'Release v1.x.x'"
            echo "   git push origin v1.x.x"
            print_warning "Production deployment requires manual approval"
            ;;
    esac
}

# Check environment status
check_status() {
    local env=$1
    local url=$(get_env_url $env)
    
    print_info "Checking $env environment status..."
    
    if [ "$url" = "unknown" ]; then
        print_error "Unknown environment: $env"
        exit 1
    fi
    
    # Health check
    if curl -f -s "$url/health" > /dev/null; then
        print_status "$env environment is healthy"
        
        # Get detailed health info
        health_info=$(curl -s "$url/health" | python -m json.tool 2>/dev/null || echo "Could not parse health response")
        echo "$health_info"
    else
        print_error "$env environment is not responding"
        
        if [ "$env" = "dev" ]; then
            print_info "Try starting the development environment:"
            echo "   ./scripts/deploy-dev.sh"
        fi
    fi
}

# View logs
view_logs() {
    local env=$1
    print_info "Viewing $env environment logs..."
    
    case $env in
        "dev")
            if [ -f "docker-compose.yml" ] || [ -f "environments/dev/docker-compose.dev.yml" ]; then
                docker-compose -f environments/dev/docker-compose.dev.yml logs -f --tail=50
            elif [ -f "logs/app.log" ]; then
                tail -f logs/app.log
            else
                print_warning "No logs found. Is the development environment running?"
            fi
            ;;
            
        "staging")
            if command -v aws &> /dev/null; then
                aws logs tail /aws/ecs/chatbot-staging --follow
            else
                print_error "AWS CLI not installed. Cannot view staging logs."
                print_info "Install AWS CLI: https://aws.amazon.com/cli/"
            fi
            ;;
            
        "prod")
            if command -v aws &> /dev/null; then
                aws logs tail /aws/ecs/chatbot-prod --follow
            else
                print_error "AWS CLI not installed. Cannot view production logs."
                print_info "Install AWS CLI: https://aws.amazon.com/cli/"
            fi
            ;;
    esac
}

# Run tests
run_tests() {
    local env=$1
    local url=$(get_env_url $env)
    
    print_info "Running tests against $env environment..."
    
    if [ "$url" = "unknown" ]; then
        print_error "Unknown environment: $env"
        exit 1
    fi
    
    # Basic health check
    if ! curl -f -s "$url/health" > /dev/null; then
        print_error "$env environment is not responding"
        exit 1
    fi
    
    # Run appropriate tests
    case $env in
        "dev")
            print_info "Running unit tests..."
            python -m pytest tests/unit/ -v
            
            print_info "Running integration tests..."
            python -m pytest tests/integration/ --base-url="$url" -v
            ;;
            
        "staging")
            print_info "Running staging test suite..."
            python -m pytest tests/integration/ --base-url="$url" -v
            python -m pytest tests/performance/ --base-url="$url" -v
            ;;
            
        "prod")
            print_info "Running production smoke tests..."
            python -m pytest tests/smoke/ --base-url="$url" -v
            ;;
    esac
}

# Switch local environment
switch_environment() {
    local env=$1
    print_info "Switching to $env environment configuration..."
    
    case $env in
        "dev")
            if [ -f "environments/dev/.env.dev" ]; then
                cp environments/dev/.env.dev .env
                print_status "Switched to development configuration"
                print_warning "Remember to update .env with your local settings"
            else
                print_error "Development environment template not found"
            fi
            ;;
            
        "staging")
            print_warning "Staging environment is managed remotely"
            print_info "You cannot switch to staging configuration locally"
            print_info "Staging uses CI/CD managed environment variables"
            ;;
            
        "prod")
            print_warning "Production environment is managed by AWS Secrets Manager"
            print_info "You cannot switch to production configuration locally"
            print_info "Production secrets are never stored in local files"
            ;;
    esac
}

# Rollback environment
rollback_environment() {
    local env=$1
    print_info "Rolling back $env environment..."
    
    case $env in
        "dev")
            print_info "Development rollback options:"
            echo "1. Git reset: git reset --hard HEAD~1"
            echo "2. Redeploy: ./scripts/deploy-dev.sh"
            echo "3. Switch branch: git checkout previous-working-branch"
            ;;
            
        "staging")
            print_info "Staging rollback options:"
            echo "1. Revert commit: git revert HEAD && git push origin develop"
            echo "2. Reset to previous: git reset --hard HEAD~1 && git push --force origin develop"
            print_warning "Force push will trigger automatic redeployment"
            ;;
            
        "prod")
            if [ -f "scripts/rollback-production.sh" ]; then
                print_warning "Production rollback requires careful consideration"
                read -p "Enter the version to rollback to (e.g., v1.1.0): " version
                if [ -n "$version" ]; then
                    chmod +x scripts/rollback-production.sh
                    ./scripts/rollback-production.sh "$version"
                fi
            else
                print_error "Production rollback script not found"
            fi
            ;;
    esac
}

# Main script logic
main() {
    local command=$1
    local environment=$2
    
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    case $command in
        "help"|"-h"|"--help")
            show_help
            ;;
        "setup")
            if [ -z "$environment" ]; then
                print_error "Environment required for setup command"
                echo "Usage: $0 setup [dev|staging|prod]"
                exit 1
            fi
            setup_environment "$environment"
            ;;
        "deploy")
            if [ -z "$environment" ]; then
                print_error "Environment required for deploy command"
                echo "Usage: $0 deploy [dev|staging|prod]"
                exit 1
            fi
            deploy_environment "$environment"
            ;;
        "status")
            if [ -z "$environment" ]; then
                print_error "Environment required for status command"
                echo "Usage: $0 status [dev|staging|prod]"
                exit 1
            fi
            check_status "$environment"
            ;;
        "logs")
            if [ -z "$environment" ]; then
                print_error "Environment required for logs command"
                echo "Usage: $0 logs [dev|staging|prod]"
                exit 1
            fi
            view_logs "$environment"
            ;;
        "test")
            if [ -z "$environment" ]; then
                print_error "Environment required for test command"
                echo "Usage: $0 test [dev|staging|prod]"
                exit 1
            fi
            run_tests "$environment"
            ;;
        "switch")
            if [ -z "$environment" ]; then
                print_error "Environment required for switch command"
                echo "Usage: $0 switch [dev|staging|prod]"
                exit 1
            fi
            switch_environment "$environment"
            ;;
        "rollback")
            if [ -z "$environment" ]; then
                print_error "Environment required for rollback command"
                echo "Usage: $0 rollback [dev|staging|prod]"
                exit 1
            fi
            rollback_environment "$environment"
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
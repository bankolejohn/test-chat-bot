#!/bin/bash
# Production Docker Helper Script

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo "🐳 3MTT Chatbot - Production Docker Setup"
echo "========================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    print_error "No .env file found. Please create one with production settings."
    echo "You can copy from .env.production template:"
    echo "cp .env.production .env"
    exit 1
fi

# Function to show usage
show_usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start     - Start production containers"
    echo "  stop      - Stop production containers"
    echo "  restart   - Restart production containers"
    echo "  logs      - Show container logs"
    echo "  status    - Show container status"
    echo "  health    - Check application health"
    echo "  backup    - Backup application data"
    echo "  build     - Rebuild production image"
    echo "  deploy    - Full production deployment"
    echo "  clean     - Remove containers and images"
    echo ""
}

# Parse command
case "${1:-start}" in
    "start")
        print_info "Starting production containers..."
        docker-compose --profile production up -d
        print_status "Production containers started!"
        print_info "🌐 Application: http://localhost:8000"
        print_info "📊 Admin Panel: http://localhost:8000/admin/analytics"
        print_info "🏥 Health Check: http://localhost:8000/health"
        print_info "📝 View logs: ./docker-prod.sh logs"
        ;;
    
    "stop")
        print_info "Stopping production containers..."
        docker-compose --profile production stop
        print_status "Production containers stopped!"
        ;;
    
    "restart")
        print_info "Restarting production containers..."
        docker-compose --profile production restart
        print_status "Production containers restarted!"
        ;;
    
    "logs")
        print_info "Showing container logs (Ctrl+C to exit)..."
        docker-compose --profile production logs -f
        ;;
    
    "status")
        print_info "Container status:"
        docker-compose --profile production ps
        ;;
    
    "health")
        print_info "Checking application health..."
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            print_status "Application is healthy!"
            curl -s http://localhost:8000/health | python -m json.tool
        else
            print_error "Application health check failed!"
            exit 1
        fi
        ;;
    
    "backup")
        print_info "Creating backup..."
        timestamp=$(date +%Y%m%d_%H%M%S)
        docker-compose exec chatbot-prod tar -czf /app/backups/backup_$timestamp.tar.gz \
            /app/conversations.json /app/training_data.json /app/knowledge_base.json
        print_status "Backup created: backup_$timestamp.tar.gz"
        ;;
    
    "build")
        print_info "Rebuilding production image..."
        docker-compose build chatbot-prod
        print_status "Production image rebuilt!"
        ;;
    
    "deploy")
        print_info "Running full production deployment..."
        
        # Build images
        docker-compose build chatbot-prod
        
        # Run tests
        print_info "Running tests..."
        docker run --rm -v $(pwd):/app -w /app python:3.11-slim bash -c "
            pip install -r requirements.txt pytest pytest-flask &&
            python run_tests.py
        "
        
        if [ $? -ne 0 ]; then
            print_error "Tests failed! Deployment aborted."
            exit 1
        fi
        
        # Start services
        docker-compose --profile production up -d
        
        # Wait for health check
        print_info "Waiting for application to be ready..."
        for i in {1..30}; do
            if curl -f http://localhost:8000/health > /dev/null 2>&1; then
                print_status "Application is ready!"
                break
            fi
            sleep 2
        done
        
        print_status "Production deployment complete!"
        ;;
    
    "clean")
        print_info "Cleaning up containers and images..."
        docker-compose --profile production down
        docker-compose down --rmi all --volumes --remove-orphans
        print_status "Cleanup complete!"
        ;;
    
    "help"|"-h"|"--help")
        show_usage
        ;;
    
    *)
        echo "❌ Unknown command: $1"
        show_usage
        exit 1
        ;;
esac
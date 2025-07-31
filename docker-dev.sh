#!/bin/bash
# Development Docker Helper Script

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

echo "🐳 3MTT Chatbot - Development Docker Setup"
echo "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Function to show usage
show_usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start     - Start development container"
    echo "  stop      - Stop development container"
    echo "  restart   - Restart development container"
    echo "  logs      - Show container logs"
    echo "  shell     - Open shell in container"
    echo "  test      - Run tests in container"
    echo "  build     - Rebuild development image"
    echo "  clean     - Remove containers and images"
    echo ""
}

# Parse command
case "${1:-start}" in
    "start")
        print_info "Starting development container..."
        docker-compose up -d chatbot-dev
        print_status "Development container started!"
        print_info "🌐 Chat Interface: http://localhost:5000"
        print_info "📊 Admin Panel: http://localhost:5000/admin/analytics"
        print_info "🏥 Health Check: http://localhost:5000/health"
        print_info "📝 View logs: ./docker-dev.sh logs"
        ;;
    
    "stop")
        print_info "Stopping development container..."
        docker-compose stop chatbot-dev
        print_status "Development container stopped!"
        ;;
    
    "restart")
        print_info "Restarting development container..."
        docker-compose restart chatbot-dev
        print_status "Development container restarted!"
        ;;
    
    "logs")
        print_info "Showing container logs (Ctrl+C to exit)..."
        docker-compose logs -f chatbot-dev
        ;;
    
    "shell")
        print_info "Opening shell in development container..."
        docker-compose exec chatbot-dev /bin/bash
        ;;
    
    "test")
        print_info "Running tests in development container..."
        docker-compose exec chatbot-dev python run_tests.py
        ;;
    
    "build")
        print_info "Rebuilding development image..."
        docker-compose build chatbot-dev
        print_status "Development image rebuilt!"
        ;;
    
    "clean")
        print_info "Cleaning up containers and images..."
        docker-compose down
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
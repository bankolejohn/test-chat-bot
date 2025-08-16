#!/bin/bash
# Branch Management Script for 3MTT Chatbot

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
    echo "🌳 3MTT Chatbot Branch Manager"
    echo "============================="
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  start-feature <name>  - Start a new feature branch"
    echo "  finish-feature        - Finish current feature branch"
    echo "  start-hotfix <name>   - Start a hotfix branch"
    echo "  finish-hotfix         - Finish current hotfix branch"
    echo "  promote-staging       - Promote develop to main (staging → prod)"
    echo "  status               - Show branch status and environment mapping"
    echo "  sync                 - Sync current branch with upstream"
    echo "  cleanup              - Clean up merged branches"
    echo ""
    echo "Examples:"
    echo "  $0 start-feature add-voice-support"
    echo "  $0 finish-feature"
    echo "  $0 start-hotfix security-patch"
    echo "  $0 promote-staging"
    echo ""
}

# Get current branch
get_current_branch() {
    git branch --show-current
}

# Check if branch exists
branch_exists() {
    git show-ref --verify --quiet refs/heads/$1
}

# Start feature branch
start_feature() {
    local feature_name=$1
    
    if [ -z "$feature_name" ]; then
        print_error "Feature name is required"
        echo "Usage: $0 start-feature <feature-name>"
        exit 1
    fi
    
    local branch_name="feature/$feature_name"
    
    print_info "Starting feature branch: $branch_name"
    
    # Ensure we're on develop and it's up to date
    git checkout develop
    git pull origin develop
    
    # Check if feature branch already exists
    if branch_exists "$branch_name"; then
        print_warning "Feature branch $branch_name already exists"
        git checkout "$branch_name"
        git pull origin "$branch_name" 2>/dev/null || true
    else
        # Create new feature branch
        git checkout -b "$branch_name"
        git push -u origin "$branch_name"
    fi
    
    print_status "Feature branch $branch_name is ready!"
    print_info "Environment: Development (http://localhost:5000)"
    print_info "Deploy with: ./scripts/env-manager.sh deploy dev"
}

# Finish feature branch
finish_feature() {
    local current_branch=$(get_current_branch)
    
    if [[ ! "$current_branch" == feature/* ]]; then
        print_error "Not on a feature branch. Current branch: $current_branch"
        exit 1
    fi
    
    print_info "Finishing feature branch: $current_branch"
    
    # Push latest changes
    git push origin "$current_branch"
    
    # Switch to develop
    git checkout develop
    git pull origin develop
    
    print_status "Feature branch $current_branch is ready for PR!"
    print_info "Next steps:"
    echo "  1. Create PR: $current_branch → develop"
    echo "  2. After approval, merge will deploy to staging"
    echo "  3. GitHub URL: https://github.com/bankolejohn/test-chat-bot/compare/develop...$current_branch"
}

# Start hotfix branch
start_hotfix() {
    local hotfix_name=$1
    
    if [ -z "$hotfix_name" ]; then
        print_error "Hotfix name is required"
        echo "Usage: $0 start-hotfix <hotfix-name>"
        exit 1
    fi
    
    local branch_name="hotfix/$hotfix_name"
    
    print_warning "Starting HOTFIX branch: $branch_name"
    print_warning "Hotfixes are for EMERGENCY production fixes only!"
    
    # Ensure we're on main and it's up to date
    git checkout main
    git pull origin main
    
    # Create hotfix branch
    git checkout -b "$branch_name"
    git push -u origin "$branch_name"
    
    print_status "Hotfix branch $branch_name is ready!"
    print_warning "Test thoroughly before merging to main!"
}

# Finish hotfix branch
finish_hotfix() {
    local current_branch=$(get_current_branch)
    
    if [[ ! "$current_branch" == hotfix/* ]]; then
        print_error "Not on a hotfix branch. Current branch: $current_branch"
        exit 1
    fi
    
    print_warning "Finishing HOTFIX branch: $current_branch"
    
    # Push latest changes
    git push origin "$current_branch"
    
    print_status "Hotfix branch $current_branch is ready for emergency PR!"
    print_warning "Next steps:"
    echo "  1. Create EMERGENCY PR: $current_branch → main"
    echo "  2. Get immediate approval and merge"
    echo "  3. Tag for production deployment"
    echo "  4. Also merge back to develop to keep it in sync"
}

# Promote staging to production
promote_staging() {
    print_info "Promoting staging (develop) to production (main)..."
    
    # Ensure develop is up to date
    git checkout develop
    git pull origin develop
    
    # Ensure main is up to date
    git checkout main
    git pull origin main
    
    print_status "Ready to promote develop → main"
    print_info "Next steps:"
    echo "  1. Create PR: develop → main"
    echo "  2. After approval and merge, create release tag:"
    echo "     git tag -a v1.x.x -m 'Release v1.x.x'"
    echo "     git push origin v1.x.x"
    echo "  3. This will trigger production deployment"
    echo ""
    echo "GitHub URL: https://github.com/bankolejohn/test-chat-bot/compare/main...develop"
}

# Show branch status
show_status() {
    local current_branch=$(get_current_branch)
    
    echo "🌳 Branch Status & Environment Mapping"
    echo "======================================"
    echo ""
    echo "📍 Current Branch: $current_branch"
    echo ""
    
    # Determine environment
    case $current_branch in
        main)
            echo "🏭 Environment: Production"
            echo "🌐 URL: https://chatbot.3mtt.gov.ng"
            echo "🚀 Deployment: Manual (release tags)"
            ;;
        develop)
            echo "🧪 Environment: Staging"
            echo "🌐 URL: https://staging.3mtt-chatbot.com"
            echo "🚀 Deployment: Automatic on push"
            ;;
        feature/*)
            echo "🔧 Environment: Development"
            echo "🌐 URL: http://localhost:5000"
            echo "🚀 Deployment: ./scripts/env-manager.sh deploy dev"
            ;;
        hotfix/*)
            echo "🚨 Environment: Hotfix (Emergency)"
            echo "🌐 URL: Test locally first"
            echo "🚀 Deployment: Emergency PR to main"
            ;;
        *)
            echo "❓ Environment: Unknown"
            echo "🌐 URL: Not mapped"
            echo "🚀 Deployment: Not configured"
            ;;
    esac
    
    echo ""
    echo "📊 Branch Overview:"
    echo "  main (production)  → https://chatbot.3mtt.gov.ng"
    echo "  develop (staging)  → https://staging.3mtt-chatbot.com"
    echo "  feature/* (dev)    → http://localhost:5000"
    echo ""
    
    # Show recent branches
    echo "📋 Recent Branches:"
    git for-each-ref --format='%(refname:short) - %(committerdate:relative)' refs/heads/ | head -5
}

# Sync current branch
sync_branch() {
    local current_branch=$(get_current_branch)
    
    print_info "Syncing branch: $current_branch"
    
    # Pull latest changes
    git pull origin "$current_branch" 2>/dev/null || {
        print_warning "Could not pull from origin (branch may not exist remotely)"
    }
    
    # Sync with upstream branch
    case $current_branch in
        feature/*)
            print_info "Syncing with develop branch..."
            git fetch origin develop
            git merge origin/develop
            ;;
        hotfix/*)
            print_info "Syncing with main branch..."
            git fetch origin main
            git merge origin/main
            ;;
        develop)
            print_info "Develop branch - pulling latest changes"
            ;;
        main)
            print_info "Main branch - pulling latest changes"
            ;;
    esac
    
    print_status "Branch $current_branch is synced!"
}

# Cleanup merged branches
cleanup_branches() {
    print_info "Cleaning up merged branches..."
    
    # Update references
    git fetch --prune
    
    # Find merged branches
    merged_branches=$(git branch --merged develop | grep -E "feature/|hotfix/" | grep -v "$(get_current_branch)" || true)
    
    if [ -n "$merged_branches" ]; then
        echo "🗑️  Merged branches found:"
        echo "$merged_branches"
        echo ""
        read -p "Delete these branches? (y/n): " confirm
        
        if [ "$confirm" = "y" ]; then
            echo "$merged_branches" | xargs -n 1 git branch -d
            print_status "Merged branches cleaned up!"
        else
            print_info "Cleanup cancelled"
        fi
    else
        print_info "No merged branches to clean up"
    fi
}

# Main script logic
main() {
    local command=$1
    shift
    
    if [ $# -eq 0 ] && [ -z "$command" ]; then
        show_help
        exit 0
    fi
    
    case $command in
        "help"|"-h"|"--help")
            show_help
            ;;
        "start-feature")
            start_feature "$1"
            ;;
        "finish-feature")
            finish_feature
            ;;
        "start-hotfix")
            start_hotfix "$1"
            ;;
        "finish-hotfix")
            finish_hotfix
            ;;
        "promote-staging")
            promote_staging
            ;;
        "status")
            show_status
            ;;
        "sync")
            sync_branch
            ;;
        "cleanup")
            cleanup_branches
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
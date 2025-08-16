#!/bin/bash
# Setup Git Hooks for Multi-Branch Strategy

set -e

echo "🔧 Setting up Git hooks for 3MTT Chatbot multi-branch strategy..."

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for 3MTT Chatbot

echo "🔍 Running pre-commit checks..."

# Check for secrets in staged files
if git diff --cached --name-only | xargs grep -l "sk-[a-zA-Z0-9]\{20,\}" 2>/dev/null; then
    echo "❌ ERROR: Potential API key found in staged files!"
    echo "Please remove API keys before committing."
    exit 1
fi

# Check for .env files
if git diff --cached --name-only | grep -E "\.env$|\.env\." | grep -v "\.env\.example"; then
    echo "❌ ERROR: Environment file found in staged files!"
    echo "Environment files should not be committed."
    echo "Files found:"
    git diff --cached --name-only | grep -E "\.env$|\.env\."
    exit 1
fi

# Check for large files
large_files=$(git diff --cached --name-only | xargs ls -la 2>/dev/null | awk '$5 > 1048576 {print $9, $5}')
if [ -n "$large_files" ]; then
    echo "❌ ERROR: Large files detected (>1MB):"
    echo "$large_files"
    echo "Please use Git LFS for large files or exclude them."
    exit 1
fi

echo "✅ Pre-commit checks passed!"
EOF

# Pre-push hook
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
# Pre-push hook for 3MTT Chatbot

current_branch=$(git branch --show-current)
remote=$1
url=$2

echo "🚀 Pre-push checks for branch: $current_branch"

# Check if pushing to main branch
if [ "$current_branch" = "main" ]; then
    echo "⚠️  WARNING: You are pushing to the main branch (production)!"
    echo "This should only be done for:"
    echo "  - Merging from develop after staging approval"
    echo "  - Emergency hotfixes"
    echo ""
    read -p "Are you sure you want to push to main? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "❌ Push cancelled"
        exit 1
    fi
fi

# Check if pushing to develop branch
if [ "$current_branch" = "develop" ]; then
    echo "📋 Pushing to develop branch (staging environment)"
    echo "This will trigger automatic deployment to staging."
fi

# Check if pushing feature branch
if [[ "$current_branch" == feature/* ]]; then
    echo "🔧 Pushing feature branch (development environment)"
    echo "This will trigger automatic deployment to development."
fi

echo "✅ Pre-push checks completed!"
EOF

# Commit message hook
cat > .git/hooks/commit-msg << 'EOF'
#!/bin/bash
# Commit message hook for 3MTT Chatbot

commit_regex='^(feat|fix|docs|style|refactor|test|chore|hotfix)(\(.+\))?: .{1,50}'

if ! grep -qE "$commit_regex" "$1"; then
    echo "❌ Invalid commit message format!"
    echo ""
    echo "Commit message should follow conventional commits:"
    echo "  feat: add new feature"
    echo "  fix: fix a bug"
    echo "  docs: update documentation"
    echo "  style: formatting changes"
    echo "  refactor: code refactoring"
    echo "  test: add or update tests"
    echo "  chore: maintenance tasks"
    echo "  hotfix: emergency production fix"
    echo ""
    echo "Examples:"
    echo "  feat: add voice support to chatbot"
    echo "  fix: resolve dashboard sync issue"
    echo "  docs: update deployment guide"
    echo "  hotfix: patch security vulnerability"
    echo ""
    exit 1
fi

echo "✅ Commit message format is valid!"
EOF

# Make hooks executable
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push
chmod +x .git/hooks/commit-msg

echo "✅ Git hooks installed successfully!"
echo ""
echo "📋 Installed hooks:"
echo "  - pre-commit: Checks for secrets, env files, and large files"
echo "  - pre-push: Warns about pushing to main/develop branches"
echo "  - commit-msg: Enforces conventional commit message format"
echo ""
echo "🎯 Next steps:"
echo "  1. Test with: git commit -m 'test: verify git hooks'"
echo "  2. Setup branch protection rules on GitHub"
echo "  3. Start using feature branches: git checkout -b feature/your-feature"
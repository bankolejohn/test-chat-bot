# 📋 Daily Operations Quick Reference

## 🚀 **Quick Start Commands**

### **Environment Manager (Recommended)**
```bash
# Setup development environment
./scripts/env-manager.sh setup dev

# Deploy to development
./scripts/env-manager.sh deploy dev

# Check environment status
./scripts/env-manager.sh status dev

# View logs
./scripts/env-manager.sh logs dev

# Run tests
./scripts/env-manager.sh test dev
```

---

## 🌳 **Git Workflow Cheat Sheet**

### **Starting New Work**
```bash
# 1. Get latest code
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Make changes and test locally
./scripts/env-manager.sh deploy dev

# 4. Commit and push
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature-name
```

### **Deploying to Environments**
```bash
# Development (automatic when you push feature branch)
git push origin feature/your-feature

# Staging (merge to develop)
git checkout develop
git merge feature/your-feature
git push origin develop

# Production (create release tag)
git checkout main
git merge develop
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0
```

---

## 🎯 **Common Scenarios**

### **Scenario 1: "I want to add a new feature"**
```bash
# 1. Start feature branch
git checkout develop && git pull
git checkout -b feature/add-new-chat-feature

# 2. Develop locally
nano app.py
./scripts/env-manager.sh deploy dev
./scripts/env-manager.sh test dev

# 3. Push for review
git add . && git commit -m "feat: add new chat feature"
git push origin feature/add-new-chat-feature

# 4. Create PR: feature/add-new-chat-feature → develop
# 5. After approval, it goes to staging automatically
# 6. After staging tests pass, create PR: develop → main
# 7. Tag for production release
```

### **Scenario 2: "I want to update the knowledge base"**
```bash
# 1. Create branch
git checkout -b feature/update-knowledge-base

# 2. Edit knowledge base
nano knowledge_base.json

# 3. Test locally
./scripts/env-manager.sh deploy dev
# Test: Ask the chatbot about new information

# 4. Deploy through normal flow
git add knowledge_base.json
git commit -m "feat: add new course information"
git push origin feature/update-knowledge-base
```

### **Scenario 3: "Something is broken in production"**
```bash
# 1. Check production status
./scripts/env-manager.sh status prod

# 2. View production logs
./scripts/env-manager.sh logs prod

# 3. Create hotfix
git checkout main
git checkout -b hotfix/fix-critical-issue

# 4. Fix and test
nano app.py
./scripts/env-manager.sh deploy dev
./scripts/env-manager.sh test dev

# 5. Emergency deployment
git add . && git commit -m "hotfix: fix critical issue"
git push origin hotfix/fix-critical-issue
# Create PR directly to main (bypass staging for emergencies)
```

### **Scenario 4: "I want to test my changes in staging"**
```bash
# 1. Ensure your feature is in develop branch
git checkout develop
git merge feature/your-feature
git push origin develop

# 2. Wait for automatic staging deployment (2-3 minutes)

# 3. Test staging environment
./scripts/env-manager.sh status staging
./scripts/env-manager.sh test staging

# 4. Access staging URL
open https://staging.3mtt-chatbot.com
```

---

## 🔧 **Environment Management**

### **Development Environment**
```bash
# Setup
./scripts/env-manager.sh setup dev

# Deploy
./scripts/env-manager.sh deploy dev

# Access
http://localhost:5000

# Logs
./scripts/env-manager.sh logs dev

# Configuration
nano .env  # Edit local settings
```

### **Staging Environment**
```bash
# Deploy (automatic on develop push)
git push origin develop

# Status
./scripts/env-manager.sh status staging

# Access
https://staging.3mtt-chatbot.com

# Logs
./scripts/env-manager.sh logs staging

# Tests
./scripts/env-manager.sh test staging
```

### **Production Environment**
```bash
# Deploy (requires release tag)
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0

# Status
./scripts/env-manager.sh status prod

# Access
https://chatbot.3mtt.gov.ng

# Logs (requires AWS access)
./scripts/env-manager.sh logs prod

# Emergency rollback
./scripts/env-manager.sh rollback prod
```

---

## 🔐 **Secret Management**

### **Development Secrets**
```bash
# Copy template
cp .env.example .env

# Edit with your keys
nano .env

# Add:
SECRET_KEY=your-dev-secret-key
OPENAI_API_KEY=sk-your-dev-openai-key
```

### **Staging/Production Secrets**
```bash
# Staging: Managed by CI/CD
# Set in GitHub Actions secrets

# Production: Managed by AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id prod/chatbot/openai-key
```

---

## 📊 **Monitoring & Debugging**

### **Check All Environments**
```bash
# Quick health check script
echo "Checking all environments..."
./scripts/env-manager.sh status dev
./scripts/env-manager.sh status staging  
./scripts/env-manager.sh status prod
```

### **View Real-time Logs**
```bash
# Development
./scripts/env-manager.sh logs dev

# Staging
./scripts/env-manager.sh logs staging

# Production
./scripts/env-manager.sh logs prod
```

### **Run Tests**
```bash
# Test specific environment
./scripts/env-manager.sh test dev
./scripts/env-manager.sh test staging
./scripts/env-manager.sh test prod

# Run all tests locally
pytest tests/ -v
```

---

## 🚨 **Emergency Procedures**

### **Production is Down**
```bash
# 1. Check status
./scripts/env-manager.sh status prod

# 2. Check logs
./scripts/env-manager.sh logs prod

# 3. Rollback if needed
./scripts/env-manager.sh rollback prod

# 4. Notify team
# Send message to #production-alerts channel
```

### **Staging Deployment Failed**
```bash
# 1. Check staging logs
./scripts/env-manager.sh logs staging

# 2. Revert the problematic commit
git revert HEAD
git push origin develop

# 3. Wait for automatic redeployment
```

### **Development Environment Issues**
```bash
# 1. Restart development environment
./scripts/env-manager.sh deploy dev

# 2. Check logs
./scripts/env-manager.sh logs dev

# 3. Reset to clean state
git checkout develop
git pull origin develop
./scripts/env-manager.sh setup dev
```

---

## 📱 **Mobile/Remote Access**

### **Quick Status Check (from anywhere)**
```bash
# Check if environments are up
curl -s https://chatbot.3mtt.gov.ng/health && echo " ✅ PROD OK"
curl -s https://staging.3mtt-chatbot.com/health && echo " ✅ STAGING OK"
```

### **Remote Deployment**
```bash
# From any machine with git access
git clone https://github.com/your-org/3mtt-chatbot.git
cd 3mtt-chatbot

# Deploy to staging
git checkout develop
git pull origin develop
# Staging deploys automatically

# Deploy to production
git checkout main
git tag -a v1.x.x -m "Emergency release"
git push origin v1.x.x
```

---

## 🎯 **Best Practices Reminders**

### **Before Making Changes**
- [ ] Pull latest code: `git pull origin develop`
- [ ] Create feature branch: `git checkout -b feature/name`
- [ ] Test locally: `./scripts/env-manager.sh test dev`

### **Before Deploying to Staging**
- [ ] Code review completed
- [ ] Unit tests pass
- [ ] Local testing successful
- [ ] Feature branch merged to develop

### **Before Deploying to Production**
- [ ] Staging tests pass
- [ ] Performance tests OK
- [ ] Security scan clean
- [ ] Stakeholder approval
- [ ] Rollback plan ready

### **After Deployment**
- [ ] Health check: `./scripts/env-manager.sh status env`
- [ ] Smoke tests: `./scripts/env-manager.sh test env`
- [ ] Monitor logs for 30 minutes
- [ ] Update documentation if needed

This quick reference should cover 90% of your daily operations with the 3MTT chatbot repository!
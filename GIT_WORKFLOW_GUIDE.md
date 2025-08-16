# 🌳 Git Workflow & Environment Management Guide

## 📋 **Branch Strategy Overview**

### **Branch-to-Environment Mapping**
```
main branch        → Production Environment
develop branch     → Staging Environment  
feature/* branches → Development Environment
hotfix/* branches  → Direct to Production (emergency)
```

### **Workflow Visualization**
```
feature/new-chat-ui ──┐
                      ├─→ develop ──→ main ──→ Production
feature/better-ai   ──┘      ↓              ↗
                           Staging      Release Tag
```

---

## 🚀 **Daily Development Workflow**

### **1. Starting New Work**
```bash
# Always start from the latest develop branch
git checkout develop
git pull origin develop

# Create a feature branch
git checkout -b feature/improve-knowledge-base
# or
git checkout -b bugfix/fix-dashboard-sync
# or  
git checkout -b hotfix/security-patch
```

### **2. Working on Your Feature**
```bash
# Make your changes
nano app.py
nano knowledge_base.json

# Test locally (this uses dev environment)
python app.py
# or
./scripts/deploy-dev.sh

# Commit your changes
git add .
git commit -m "feat: improve knowledge base search algorithm"

# Push to your feature branch
git push origin feature/improve-knowledge-base
```

### **3. Getting Your Changes to Staging**
```bash
# Create Pull Request: feature/improve-knowledge-base → develop
# After code review and approval, merge to develop

# This automatically triggers deployment to STAGING
git checkout develop
git pull origin develop  # Now has your changes
```

### **4. Getting Your Changes to Production**
```bash
# Create Pull Request: develop → main
# After thorough testing in staging

# Create a release tag for production
git checkout main
git pull origin main
git tag -a v1.2.0 -m "Release v1.2.0: Improved knowledge base"
git push origin v1.2.0

# This triggers production deployment with manual approval
```

---

## 🎯 **Environment-Specific Operations**

### **🔧 Development Environment**

#### **Deploy to Development**
```bash
# Option 1: Automatic (when you push to feature branch)
git push origin feature/my-feature

# Option 2: Manual local deployment
./scripts/deploy-dev.sh

# Option 3: Docker local development
cd environments/dev/
docker-compose -f docker-compose.dev.yml up --build
```

#### **Test in Development**
```bash
# Access development environment
curl http://localhost:5000/health

# View logs
docker-compose -f environments/dev/docker-compose.dev.yml logs -f

# Run tests
pytest tests/ -v
```

#### **Development Environment Variables**
```bash
# Copy dev template
cp environments/dev/.env.dev .env

# Edit for local development
nano .env
# Set: SECRET_KEY=dev-key, OPENAI_API_KEY=your-key, etc.
```

### **🧪 Staging Environment**

#### **Deploy to Staging**
```bash
# Automatic: Push to develop branch
git checkout develop
git merge feature/my-feature
git push origin develop

# Manual: Run staging deployment
./scripts/deploy-staging.sh
```

#### **Test in Staging**
```bash
# Health check
curl https://staging.3mtt-chatbot.com/health

# Run integration tests
pytest tests/integration/ --base-url=https://staging.3mtt-chatbot.com

# Performance testing
ab -n 1000 -c 50 https://staging.3mtt-chatbot.com/
```

#### **Staging Environment Management**
```bash
# View staging logs
aws logs tail /aws/ecs/chatbot-staging --follow

# Check staging database
aws rds describe-db-instances --db-instance-identifier staging-chatbot-db

# Monitor staging metrics
curl https://staging.3mtt-chatbot.com:9090/metrics
```

### **🏭 Production Environment**

#### **Deploy to Production**
```bash
# Create release (requires approval)
git checkout main
git merge develop
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0

# Manual production deployment (with approval)
./scripts/deploy-production.sh
```

#### **Production Operations**
```bash
# Health check
curl https://chatbot.3mtt.gov.ng/health

# View production logs
aws logs tail /aws/ecs/chatbot-prod --follow

# Check production metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=chatbot-prod
```

---

## 📂 **Repository Structure Management**

### **What Goes Where**
```
3mtt-chatbot/
├── app.py                    # ✅ Commit (main application)
├── knowledge_base.json       # ✅ Commit (shared knowledge)
├── requirements*.txt         # ✅ Commit (dependencies)
├── Dockerfile               # ✅ Commit (containerization)
├── .env.example             # ✅ Commit (template)
├── .env                     # ❌ Don't commit (local secrets)
├── conversations.json       # ❌ Don't commit (user data)
├── logs/                    # ❌ Don't commit (runtime data)
└── environments/
    ├── dev/
    │   ├── .env.dev         # ❌ Don't commit (dev secrets)
    │   └── docker-compose.dev.yml  # ✅ Commit (dev config)
    ├── staging/
    │   ├── .env.staging     # ❌ Don't commit (staging secrets)
    │   └── docker-compose.staging.yml  # ✅ Commit
    └── production/
        ├── .env.production  # ❌ Don't commit (prod secrets)
        └── terraform/       # ✅ Commit (infrastructure)
```

### **Environment Configuration Management**
```bash
# Each environment has its own config
# DEV: Use .env.dev template, customize locally
cp environments/dev/.env.dev .env
nano .env  # Add your local settings

# STAGING: Managed by deployment scripts
# Uses AWS Secrets Manager or environment variables

# PRODUCTION: Managed by AWS Secrets Manager
# Never store production secrets in files
```

---

## 🔄 **Common Workflows**

### **Scenario 1: Adding a New Feature**
```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/add-voice-support

# 3. Develop and test locally (DEV environment)
# Edit code, test with ./scripts/deploy-dev.sh

# 4. Commit and push
git add .
git commit -m "feat: add voice support to chatbot"
git push origin feature/add-voice-support

# 5. Create PR to develop (triggers STAGING deployment)
# 6. After testing in staging, create PR to main
# 7. Tag release for PRODUCTION deployment
```

### **Scenario 2: Hotfix for Production**
```bash
# 1. Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/security-patch

# 2. Make critical fix
nano app.py  # Fix security issue

# 3. Test quickly in dev
./scripts/deploy-dev.sh

# 4. Fast-track to production
git add .
git commit -m "hotfix: patch security vulnerability"
git push origin hotfix/security-patch

# 5. Create PR directly to main (bypass staging for critical fixes)
# 6. Emergency production deployment
```

### **Scenario 3: Updating Knowledge Base**
```bash
# 1. Create feature branch
git checkout -b feature/update-knowledge-base

# 2. Update knowledge base
nano knowledge_base.json

# 3. Test in development
python app.py
# Test: "What are the new course requirements?"

# 4. Commit and deploy through normal flow
git add knowledge_base.json
git commit -m "feat: add new course requirements to knowledge base"
git push origin feature/update-knowledge-base

# 5. PR to develop → staging → main → production
```

### **Scenario 4: Environment-Specific Configuration**
```bash
# Different configs for different environments

# Development (local)
echo "OPENAI_API_KEY=your-dev-key" > .env
echo "LOG_LEVEL=DEBUG" >> .env

# Staging (managed by CI/CD)
# Uses environments/staging/.env.staging template
# Secrets injected by deployment pipeline

# Production (AWS Secrets Manager)
# No local files, all secrets managed by AWS
aws secretsmanager get-secret-value --secret-id prod/chatbot/openai-key
```

---

## 🔐 **Secret Management Per Environment**

### **Development (Local)**
```bash
# Use local .env file (not committed)
cp .env.example .env
nano .env

# Add your development keys
SECRET_KEY=dev-secret-key-123
OPENAI_API_KEY=your-dev-key-here
```

### **Staging**
```bash
# Managed by deployment scripts
# Secrets stored in CI/CD environment variables
export STAGING_SECRET_KEY="staging-secure-key"
export STAGING_OPENAI_KEY="your-staging-key"
```

### **Production**
```bash
# Managed by AWS Secrets Manager
aws secretsmanager create-secret \
  --name "prod/chatbot/secret-key" \
  --secret-string "ultra-secure-production-key"

aws secretsmanager create-secret \
  --name "prod/chatbot/openai-key" \
  --secret-string "your-production-openai-key"
```

---

## 📊 **Monitoring Your Deployments**

### **Check Deployment Status**
```bash
# Development
curl http://localhost:5000/health

# Staging  
curl https://staging.3mtt-chatbot.com/health

# Production
curl https://chatbot.3mtt.gov.ng/health
```

### **View Environment Logs**
```bash
# Development
docker-compose -f environments/dev/docker-compose.dev.yml logs -f

# Staging
aws logs tail /aws/ecs/chatbot-staging --follow

# Production
aws logs tail /aws/ecs/chatbot-prod --follow
```

### **Rollback if Needed**
```bash
# Staging rollback
git revert HEAD
git push origin develop

# Production rollback
./scripts/rollback-production.sh v1.1.0
```

---

## 🎯 **Quick Reference Commands**

### **Daily Development**
```bash
# Start new work
git checkout develop && git pull && git checkout -b feature/my-feature

# Test locally
./scripts/deploy-dev.sh

# Deploy to staging
git push origin develop

# Deploy to production
git tag v1.x.x && git push origin v1.x.x
```

### **Environment Access**
```bash
# DEV:     http://localhost:5000
# STAGING: https://staging.3mtt-chatbot.com  
# PROD:    https://chatbot.3mtt.gov.ng
```

### **Emergency Procedures**
```bash
# Production hotfix
git checkout main && git checkout -b hotfix/critical-fix

# Emergency rollback
./scripts/rollback-production.sh

# Check all environments
curl -s http://localhost:5000/health && echo " - DEV OK"
curl -s https://staging.3mtt-chatbot.com/health && echo " - STAGING OK"  
curl -s https://chatbot.3mtt.gov.ng/health && echo " - PROD OK"
```

This workflow ensures clean separation between environments while maintaining proper version control and deployment practices.
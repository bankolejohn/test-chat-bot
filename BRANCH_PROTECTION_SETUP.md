# 🛡️ Branch Protection Rules Setup

## 📋 **GitHub Branch Protection Configuration**

To complete the multi-branch strategy, you need to set up branch protection rules on GitHub:

### **1. Go to GitHub Repository Settings**
1. Navigate to your repository: https://github.com/bankolejohn/test-chat-bot
2. Click on **Settings** tab
3. Click on **Branches** in the left sidebar

### **2. Protect `main` Branch (Production)**
Click **Add rule** and configure:

```
Branch name pattern: main

☑️ Require a pull request before merging
  ☑️ Require approvals (1)
  ☑️ Dismiss stale PR approvals when new commits are pushed
  ☑️ Require review from code owners

☑️ Require status checks to pass before merging
  ☑️ Require branches to be up to date before merging
  Status checks to require:
    - ci (GitHub Actions CI)
    - security-scan
    - tests

☑️ Require conversation resolution before merging
☑️ Require signed commits (optional but recommended)
☑️ Include administrators
☑️ Restrict pushes that create files larger than 100MB
```

### **3. Protect `develop` Branch (Staging)**
Click **Add rule** and configure:

```
Branch name pattern: develop

☑️ Require a pull request before merging
  ☑️ Require approvals (1)

☑️ Require status checks to pass before merging
  ☑️ Require branches to be up to date before merging
  Status checks to require:
    - ci (GitHub Actions CI)
    - tests

☑️ Require conversation resolution before merging
☑️ Include administrators
```

### **4. Set Default Branch**
1. In Repository Settings → General
2. Set **Default branch** to `develop`
3. This ensures new PRs target develop by default

## 🔄 **Workflow Rules Summary**

### **Branch Hierarchy**
```
main (Production)
  ↑
develop (Staging)  
  ↑
feature/* (Development)
```

### **Merge Rules**
- **feature/* → develop**: Requires 1 approval + CI pass
- **develop → main**: Requires 1 approval + all checks pass
- **hotfix/* → main**: Emergency only, requires approval

### **Deployment Triggers**
- **Push to develop**: Auto-deploy to staging
- **Tag on main**: Manual approval → deploy to production
- **Push to feature/***: Auto-deploy to dev environment

## 🚀 **After Setting Up Protection Rules**

Run this command to verify your setup:
```bash
./scripts/env-manager.sh status dev
```

Your multi-branch strategy will be fully active!
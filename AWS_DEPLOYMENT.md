# AWS Production Deployment Guide

## 🏗️ Architecture Overview

This deployment uses a modern, scalable AWS architecture:

- **ECS Fargate** - Serverless container orchestration
- **Application Load Balancer** - High availability and SSL termination
- **RDS PostgreSQL** - Managed database with automated backups
- **ElastiCache Redis** - In-memory caching and session storage
- **ECR** - Container registry for Docker images
- **VPC** - Isolated network with public/private subnets
- **SSM Parameter Store** - Secure secrets management
- **CloudWatch** - Logging and monitoring
- **GitHub Actions** - CI/CD pipeline

## 📋 Prerequisites

### Required Tools
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### AWS Account Setup
1. **Create AWS Account** with billing enabled
2. **Create IAM User** with programmatic access
3. **Attach Policies**:
   - `AmazonECS_FullAccess`
   - `AmazonRDS_FullAccess`
   - `AmazonElastiCacheFullAccess`
   - `AmazonEC2FullAccess`
   - `AmazonS3FullAccess`
   - `IAMFullAccess`
   - `AmazonSSMFullAccess`

### Configure AWS CLI
```bash
aws configure
# AWS Access Key ID: [Your Access Key]
# AWS Secret Access Key: [Your Secret Key]
# Default region name: us-east-1
# Default output format: json
```

## 🚀 Deployment Methods

### Method 1: Automated Script (Recommended)

```bash
# 1. Clone repository
git clone <your-repo-url>
cd test-chatbot

# 2. Configure variables
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
nano terraform/terraform.tfvars

# 3. Run deployment script
./scripts/deploy.sh
```

### Method 2: Manual Terraform Deployment

```bash
# 1. Create S3 bucket for Terraform state
aws s3 mb s3://3mtt-chatbot-terraform-state --region us-east-1

# 2. Initialize Terraform
cd terraform
terraform init

# 3. Plan deployment
terraform plan

# 4. Apply infrastructure
terraform apply

# 5. Build and push Docker image
ECR_URL=$(terraform output -raw ecr_repository_url)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_URL
docker build -t 3mtt-chatbot .
docker tag 3mtt-chatbot:latest $ECR_URL:latest
docker push $ECR_URL:latest

# 6. Update ECS service
aws ecs update-service --cluster 3mtt-chatbot --service 3mtt-chatbot --force-new-deployment
```

### Method 3: GitHub Actions CI/CD

```bash
# 1. Set up GitHub repository secrets
# Go to Settings > Secrets and variables > Actions

# Required secrets:
AWS_ROLE_ARN=arn:aws:iam::ACCOUNT-ID:role/3mtt-chatbot-github-actions-role

# 2. Push to main branch triggers deployment
git push origin main
```

## 🔧 Configuration

### Environment Variables
Create `terraform/terraform.tfvars`:

```hcl
aws_region = "us-east-1"
db_password = "SuperSecurePassword123!"
openai_api_key = "your-openai-key"
secret_key = "your-32-char-secret-key"
sentry_dsn = "https://your-sentry-dsn"
```

### Generate Secure Keys
```bash
# Generate Flask secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Generate database password
openssl rand -base64 32
```

## 📊 Monitoring & Observability

### CloudWatch Logs
```bash
# View application logs
aws logs tail /ecs/3mtt-chatbot --follow

# View specific log stream
aws logs describe-log-streams --log-group-name /ecs/3mtt-chatbot
```

### Health Checks
```bash
# Application health
curl http://your-alb-dns/health

# Database connectivity
aws rds describe-db-instances --db-instance-identifier 3mtt-chatbot-db

# Redis connectivity
aws elasticache describe-cache-clusters --cache-cluster-id 3mtt-chatbot-redis
```

### Metrics Dashboard
Access CloudWatch metrics:
- ECS Service metrics
- ALB request metrics
- RDS performance metrics
- ElastiCache metrics

## 🔒 Security Best Practices

### Network Security
- **VPC Isolation** - Private subnets for database and cache
- **Security Groups** - Least privilege access rules
- **NAT Gateway** - Outbound internet access for private subnets

### Data Security
- **Encryption at Rest** - RDS and ElastiCache encryption
- **Encryption in Transit** - SSL/TLS for all connections
- **Secrets Management** - SSM Parameter Store for sensitive data

### Access Control
- **IAM Roles** - Service-specific permissions
- **JWT Authentication** - Admin endpoint protection
- **Rate Limiting** - DDoS protection

## 💰 Cost Optimization

### Resource Sizing
- **ECS Fargate**: 0.5 vCPU, 1GB RAM (~$15/month)
- **RDS t3.micro**: (~$15/month)
- **ElastiCache t3.micro**: (~$12/month)
- **ALB**: (~$20/month)
- **Total**: ~$62/month

### Cost Reduction Tips
```bash
# Use Spot instances for development
# Enable RDS automated backups retention (7 days)
# Use CloudWatch log retention policies
# Monitor with AWS Cost Explorer
```

## 🔄 Scaling & Performance

### Auto Scaling
```hcl
# Add to ECS service
resource "aws_appautoscaling_target" "ecs_target" {
  max_capacity       = 10
  min_capacity       = 2
  resource_id        = "service/3mtt-chatbot/3mtt-chatbot"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}
```

### Database Scaling
```bash
# Increase RDS instance size
aws rds modify-db-instance \
  --db-instance-identifier 3mtt-chatbot-db \
  --db-instance-class db.t3.small \
  --apply-immediately
```

## 🐛 Troubleshooting

### Common Issues

**ECS Service Won't Start**
```bash
# Check service events
aws ecs describe-services --cluster 3mtt-chatbot --services 3mtt-chatbot

# Check task definition
aws ecs describe-task-definition --task-definition 3mtt-chatbot
```

**Database Connection Issues**
```bash
# Check security groups
aws ec2 describe-security-groups --group-names 3mtt-chatbot-rds-*

# Test connectivity from ECS task
aws ecs execute-command --cluster 3mtt-chatbot --task TASK-ID --interactive --command "/bin/bash"
```

**High Memory Usage**
```bash
# Scale up ECS service
aws ecs update-service --cluster 3mtt-chatbot --service 3mtt-chatbot --desired-count 4

# Increase task memory
# Update task definition with more memory allocation
```

### Logs Analysis
```bash
# Application errors
aws logs filter-log-events --log-group-name /ecs/3mtt-chatbot --filter-pattern "ERROR"

# Performance metrics
aws logs filter-log-events --log-group-name /ecs/3mtt-chatbot --filter-pattern "response_time"
```

## 🔄 Updates & Maintenance

### Application Updates
```bash
# Automated via GitHub Actions
git push origin main

# Manual update
docker build -t 3mtt-chatbot .
docker tag 3mtt-chatbot:latest $ECR_URL:latest
docker push $ECR_URL:latest
aws ecs update-service --cluster 3mtt-chatbot --service 3mtt-chatbot --force-new-deployment
```

### Infrastructure Updates
```bash
cd terraform
terraform plan
terraform apply
```

### Database Maintenance
```bash
# Manual backup
aws rds create-db-snapshot \
  --db-instance-identifier 3mtt-chatbot-db \
  --db-snapshot-identifier 3mtt-chatbot-manual-backup-$(date +%Y%m%d)

# Restore from backup
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier 3mtt-chatbot-db-restored \
  --db-snapshot-identifier 3mtt-chatbot-manual-backup-20231201
```

## 🧹 Cleanup

### Destroy Infrastructure
```bash
# Terraform destroy
cd terraform
terraform destroy

# Manual cleanup
aws s3 rm s3://3mtt-chatbot-terraform-state --recursive
aws s3 rb s3://3mtt-chatbot-terraform-state
```

## 📞 Support

### Monitoring Alerts
Set up CloudWatch alarms for:
- High CPU usage (>80%)
- High memory usage (>80%)
- Database connections (>80% of max)
- Application errors (>10/minute)

### Emergency Procedures
```bash
# Scale down in emergency
aws ecs update-service --cluster 3mtt-chatbot --service 3mtt-chatbot --desired-count 0

# Database failover (if Multi-AZ enabled)
aws rds reboot-db-instance --db-instance-identifier 3mtt-chatbot-db --force-failover
```

## 🎯 Production Checklist

- [ ] AWS account configured with proper IAM permissions
- [ ] Domain name registered and DNS configured
- [ ] SSL certificate obtained (AWS Certificate Manager)
- [ ] Monitoring and alerting configured
- [ ] Backup strategy implemented
- [ ] Security groups reviewed and hardened
- [ ] Cost monitoring enabled
- [ ] Disaster recovery plan documented
- [ ] Team access and permissions configured
- [ ] Documentation updated and shared

---

**🎉 Your 3MTT Chatbot is now running on AWS with enterprise-grade infrastructure!**

Access your application at: `http://your-alb-dns-name`
# ☁️ AWS Deployment Guide for 3MTT Chatbot

## 🎯 AWS Deployment Options Comparison

| Option | Difficulty | Cost | Scalability | Best For |
|--------|------------|------|-------------|----------|
| **Elastic Beanstalk** | Easy | $5-20/month | High | Beginners |
| **App Runner** | Easy | $2-10/month | Medium | Container fans |
| **Lambda + API Gateway** | Medium | $0-5/month | Very High | Serverless |
| **EC2** | Hard | $5-50/month | Very High | Full control |

---

## 🟢 Option 1: AWS Elastic Beanstalk (Recommended)

**Why Elastic Beanstalk?**
- Easiest AWS deployment
- Handles load balancing, auto-scaling
- Built-in monitoring
- Easy rollbacks

### Steps:
1. **Install AWS CLI & EB CLI**
   ```bash
   # Install AWS CLI
   curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
   sudo installer -pkg AWSCLIV2.pkg -target /
   
   # Install EB CLI
   pip install awsebcli
   ```

2. **Configure AWS Credentials**
   ```bash
   aws configure
   # Enter your AWS Access Key ID
   # Enter your AWS Secret Access Key
   # Default region: us-east-1
   # Default output format: json
   ```

3. **Initialize Elastic Beanstalk**
   ```bash
   eb init
   # Select region
   # Create new application: 3mtt-chatbot
   # Select Python 3.11
   # Setup SSH: Yes
   ```

4. **Create Environment**
   ```bash
   eb create production
   # Wait 5-10 minutes for environment creation
   ```

5. **Set Environment Variables**
   ```bash
   eb setenv SECRET_KEY=your-secret-key-here
   eb setenv OPENAI_API_KEY=your-openai-key-here
   ```

6. **Deploy**
   ```bash
   eb deploy
   ```

7. **Open Your App**
   ```bash
   eb open
   ```

**Your chatbot will be live at**: `http://your-app.region.elasticbeanstalk.com`

---

## 🟡 Option 2: AWS App Runner (Container-based)

**Why App Runner?**
- Fully managed containers
- Auto-scaling
- Pay per use
- Easy CI/CD

### Steps:
1. **Create GitHub Repository** (same as Heroku process)
2. **Go to AWS App Runner Console**
3. **Create Service**
   - Source: GitHub
   - Repository: your-3mtt-chatbot
   - Branch: main
   - Build settings: Automatic
4. **Configure Service**
   - Service name: 3mtt-chatbot
   - Virtual CPU: 0.25 vCPU
   - Memory: 0.5 GB
5. **Set Environment Variables**
   - SECRET_KEY: your-secret-key
   - OPENAI_API_KEY: your-openai-key
6. **Deploy**

---

## 🟠 Option 3: AWS Lambda (Serverless)

**Why Lambda?**
- Pay only when used
- Automatic scaling
- No server management
- Very cost-effective

### Steps:
1. **Install Serverless Framework**
   ```bash
   npm install -g serverless
   ```

2. **Update requirements.txt**
   ```bash
   echo "serverless-wsgi" >> requirements.txt
   ```

3. **Deploy**
   ```bash
   serverless deploy
   ```

**Your chatbot will be live at**: API Gateway URL provided after deployment

---

## 🔵 Option 4: AWS EC2 (Full Control)

**Why EC2?**
- Complete control
- Custom configurations
- Can handle high traffic
- Most cost-effective for high usage

### Steps:
1. **Launch EC2 Instance**
   - AMI: Amazon Linux 2
   - Instance Type: t3.micro (free tier)
   - Security Group: Allow HTTP (80) and SSH (22)

2. **Connect to Instance**
   ```bash
   ssh -i your-key.pem ec2-user@your-instance-ip
   ```

3. **Run Deployment Script**
   ```bash
   chmod +x deploy_ec2.sh
   ./deploy_ec2.sh
   ```

---

## 💰 Cost Comparison (Monthly)

### Light Usage (< 1000 requests/day):
- **Lambda**: $0-2
- **App Runner**: $2-5
- **Elastic Beanstalk**: $5-15
- **EC2**: $5-10

### Medium Usage (< 10,000 requests/day):
- **Lambda**: $2-10
- **App Runner**: $5-15
- **Elastic Beanstalk**: $10-25
- **EC2**: $10-20

### High Usage (> 50,000 requests/day):
- **Lambda**: $10-50
- **App Runner**: $20-50
- **Elastic Beanstalk**: $25-100
- **EC2**: $20-50

---

## 🔧 Environment Variables for All Options

Set these in your AWS service:
```
SECRET_KEY=your-random-secret-key-123456789
OPENAI_API_KEY=your-openai-key-here (optional)
```

---

## 🌐 Custom Domain Setup

### For any AWS service:
1. **Register domain** in Route 53 or use existing domain
2. **Create SSL certificate** in AWS Certificate Manager
3. **Configure CloudFront** (optional, for better performance)
4. **Update DNS records** to point to your AWS service

---

## 📊 Monitoring & Logs

### CloudWatch Integration:
- All AWS services automatically send logs to CloudWatch
- Set up alarms for errors or high usage
- Monitor response times and error rates

### Access Logs:
```bash
# Elastic Beanstalk
eb logs

# App Runner
Check AWS Console → App Runner → Logs

# Lambda
Check AWS Console → CloudWatch → Log Groups

# EC2
sudo journalctl -u 3mtt-chatbot -f
```

---

## 🚀 Recommended Deployment Path

### For Beginners:
1. **Start with Elastic Beanstalk** - easiest to set up
2. **Use GitHub integration** for easy updates
3. **Monitor costs** in AWS billing dashboard

### For Cost-Conscious:
1. **Start with Lambda** - pay only for usage
2. **Upgrade to App Runner** if you need always-on
3. **Consider EC2** for high traffic

### For Production:
1. **Use Elastic Beanstalk** with load balancer
2. **Set up CloudFront** for global distribution
3. **Configure auto-scaling** based on traffic
4. **Set up monitoring** and alerts

---

## 🔒 Security Best Practices

1. **Use IAM roles** instead of access keys when possible
2. **Enable AWS WAF** for web application firewall
3. **Use VPC** for network isolation
4. **Enable CloudTrail** for audit logging
5. **Regular security updates** for EC2 instances

---

## 🎉 Next Steps After Deployment

1. **Test your chatbot** thoroughly
2. **Set up monitoring** and alerts
3. **Configure backups** for your data
4. **Set up CI/CD pipeline** for easy updates
5. **Monitor costs** and optimize as needed

Your 3MTT chatbot will be running on enterprise-grade AWS infrastructure! 🌟
# 🔒 Security Best Practices for 3MTT Chatbot Deployment

## ⚠️ Critical Security Issues Fixed

### ❌ What NOT to do:
```bash
# NEVER put secrets directly in scripts
export SECRET_KEY="my-secret-key"
export OPENAI_API_KEY="sk-1234567890"
```

### ✅ What TO do:
```bash
# Use environment files with proper permissions
echo "SECRET_KEY=generated-secure-key" > .env
chmod 600 .env  # Only owner can read/write
```

---

## 🔐 Secure Secret Management

### 1. Environment Files (.env)
```bash
# Create secure .env file
cat > .env << EOF
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
OPENAI_API_KEY=your-actual-key-here
EOF

# Secure the file
chmod 600 .env
chown ec2-user:ec2-user .env
```

### 2. AWS Systems Manager Parameter Store
```bash
# Store secrets in AWS Parameter Store
aws ssm put-parameter \
    --name "/3mtt-chatbot/secret-key" \
    --value "your-secret-key" \
    --type "SecureString"

aws ssm put-parameter \
    --name "/3mtt-chatbot/openai-key" \
    --value "your-openai-key" \
    --type "SecureString"
```

### 3. AWS Secrets Manager
```bash
# Create secret in AWS Secrets Manager
aws secretsmanager create-secret \
    --name "3mtt-chatbot-secrets" \
    --description "Secrets for 3MTT Chatbot" \
    --secret-string '{"SECRET_KEY":"your-key","OPENAI_API_KEY":"your-openai-key"}'
```

---

## 🛡️ Deployment Security Checklist

### ✅ Environment Variables
- [ ] Never commit secrets to git
- [ ] Use .env files with 600 permissions
- [ ] Generate strong SECRET_KEY automatically
- [ ] Use AWS Parameter Store for production

### ✅ File Permissions
- [ ] .env file: 600 (owner read/write only)
- [ ] Application files: 644 (owner write, group/other read)
- [ ] Scripts: 755 (executable)
- [ ] Logs: 644 with proper rotation

### ✅ Service Security
- [ ] Run service as non-root user (ec2-user)
- [ ] Use systemd security features
- [ ] Enable PrivateTmp and ProtectSystem
- [ ] Restrict file system access

### ✅ Network Security
- [ ] Configure AWS Security Groups properly
- [ ] Use HTTPS (SSL/TLS certificates)
- [ ] Enable rate limiting in Nginx
- [ ] Add security headers

### ✅ Monitoring & Logging
- [ ] Enable CloudTrail for API logging
- [ ] Set up CloudWatch alarms
- [ ] Configure log rotation
- [ ] Monitor for suspicious activity

---

## 🔧 Secure Deployment Scripts

### Updated EC2 Deployment (Secure)
```bash
# Use the secure deployment script
chmod +x deploy_ec2_secure.sh
./deploy_ec2_secure.sh https://github.com/username/3mtt-chatbot.git
```

### Features of Secure Script:
- ✅ Generates secure SECRET_KEY automatically
- ✅ Creates .env file with proper permissions
- ✅ Runs service with restricted user permissions
- ✅ Adds Nginx security headers
- ✅ Enables rate limiting
- ✅ Sets up log rotation
- ✅ Provides update mechanism

---

## 🌐 Production Security Enhancements

### 1. SSL/TLS Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo yum install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. Firewall Configuration
```bash
# Configure iptables
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT  # SSH
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT  # HTTP
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT # HTTPS
sudo iptables -A INPUT -j DROP  # Drop all other traffic
```

### 3. AWS Security Groups
```json
{
  "SecurityGroupRules": [
    {
      "IpProtocol": "tcp",
      "FromPort": 22,
      "ToPort": 22,
      "CidrIp": "your-ip/32"
    },
    {
      "IpProtocol": "tcp", 
      "FromPort": 80,
      "ToPort": 80,
      "CidrIp": "0.0.0.0/0"
    },
    {
      "IpProtocol": "tcp",
      "FromPort": 443, 
      "ToPort": 443,
      "CidrIp": "0.0.0.0/0"
    }
  ]
}
```

---

## 🔍 Security Monitoring

### 1. Log Monitoring
```bash
# Monitor application logs
sudo journalctl -u 3mtt-chatbot -f

# Monitor Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Monitor system logs
sudo tail -f /var/log/messages
```

### 2. CloudWatch Integration
```python
# Add to your Flask app for CloudWatch logging
import boto3
import logging

cloudwatch = boto3.client('logs')
handler = CloudWatchLogsHandler(log_group='3mtt-chatbot')
logging.getLogger().addHandler(handler)
```

### 3. Security Alerts
```bash
# Set up fail2ban for SSH protection
sudo yum install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 🚨 Incident Response

### If Secrets Are Compromised:
1. **Immediately rotate all secrets**
2. **Check access logs for suspicious activity**
3. **Update .env file with new secrets**
4. **Restart services**
5. **Monitor for unusual behavior**

### Emergency Commands:
```bash
# Stop service immediately
sudo systemctl stop 3mtt-chatbot

# Rotate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))" > new_secret.txt

# Check who accessed files
sudo ausearch -f /home/ec2-user/3mtt-chatbot/.env

# Review recent logins
last -n 20
```

---

## 📋 Security Audit Checklist

### Monthly Security Review:
- [ ] Review access logs for anomalies
- [ ] Update system packages
- [ ] Rotate secrets if needed
- [ ] Check file permissions
- [ ] Review AWS CloudTrail logs
- [ ] Test backup and recovery procedures
- [ ] Verify SSL certificate expiration
- [ ] Check for security updates

### Tools for Security Scanning:
```bash
# Check for vulnerabilities
sudo yum update --security

# Scan for malware
sudo yum install -y clamav
sudo freshclam
sudo clamscan -r /home/ec2-user/3mtt-chatbot/

# Check open ports
sudo netstat -tulpn
```

---

## 🎯 Key Takeaways

1. **Never hardcode secrets** in scripts or code
2. **Use proper file permissions** (600 for secrets)
3. **Run services with minimal privileges**
4. **Enable security headers and rate limiting**
5. **Monitor logs and set up alerts**
6. **Keep systems updated**
7. **Use HTTPS in production**
8. **Regular security audits**

Your 3MTT chatbot is now deployed with enterprise-grade security! 🛡️
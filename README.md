# 3MTT Production-Ready AI Chatbot

A production-grade Flask-based chatbot for 3MTT customer support with enterprise-level security, monitoring, and scalability.

## 🚀 Production Features

### Security
- **JWT Authentication** for admin endpoints
- **Rate Limiting** with Redis backend
- **Input Sanitization** and validation
- **CORS Protection** with configurable origins
- **Security Headers** (CSP, HSTS, XSS Protection)
- **Password Hashing** with bcrypt
- **SQL Injection Protection** with SQLAlchemy ORM

### Scalability
- **PostgreSQL Database** for persistent storage
- **Redis Caching** for AI responses and sessions
- **Gunicorn WSGI Server** with multiple workers
- **Nginx Reverse Proxy** with load balancing
- **Docker Containerization** for easy deployment
- **Database Migrations** with Flask-Migrate

### Monitoring & Observability
- **Prometheus Metrics** for performance monitoring
- **Structured Logging** with JSON format
- **Sentry Integration** for error tracking
- **Health Check Endpoints** for uptime monitoring
- **Request/Response Tracking** with unique IDs

### DevOps & CI/CD
- **GitHub Actions** for automated testing and deployment
- **Docker Compose** for local development
- **Security Scanning** with Bandit and Safety
- **Automated Testing** with pytest
- **Database Migrations** in deployment pipeline

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)
- Nginx (for production)

## 🛠️ Installation & Setup

### 1. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Database Setup

```bash
# Install PostgreSQL and create database
sudo apt install postgresql postgresql-contrib
sudo -u postgres createdb chatbot_db
sudo -u postgres createuser chatbot
```

### 3. Application Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Create admin user
python -c "
from app import create_app
from models import db, AdminUser
from auth import hash_password
app = create_app()
with app.app_context():
    admin = AdminUser(username='admin', password_hash=hash_password('your_secure_password'))
    db.session.add(admin)
    db.session.commit()
"
```

### 4. Production Deployment

```bash
# Using Docker Compose (Recommended)
docker-compose up -d

# Or manual deployment
gunicorn --config gunicorn.conf.py wsgi:app
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/production) | `production` |
| `SECRET_KEY` | Flask secret key | Required |
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `OPENAI_API_KEY` | OpenAI API key | Optional |
| `SENTRY_DSN` | Sentry error tracking DSN | Optional |
| `RATE_LIMIT_PER_MINUTE` | API rate limit | `10` |

### Security Configuration

```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Hash admin password
python -c "from auth import hash_password; print(hash_password('your_password'))"
```

## 📊 Monitoring & Analytics

### Prometheus Metrics
- HTTP request metrics
- Chat interaction metrics
- AI response times
- Active session counts

Access metrics at: `http://localhost:9090/metrics`

### Health Checks
- Database connectivity
- Redis connectivity
- Disk space monitoring
- AI service status

Access health check at: `http://localhost:5000/health`

### Admin Dashboard
- Conversation analytics
- User sentiment analysis
- Performance metrics
- System status

Access admin at: `http://localhost:5000/admin/analytics`

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html

# Security scanning
bandit -r . -x tests/
safety check
```

## 🚀 Deployment Options

### Local Docker Deployment
```bash
# Build and run locally
docker-compose up -d

# Scale workers
docker-compose up -d --scale web=3
```

### AWS Production Deployment
```bash
# Automated deployment script
./scripts/deploy.sh

# Or manual Terraform deployment
cd terraform && terraform apply
```

### CI/CD with GitHub Actions
```bash
# Push to main branch triggers AWS deployment
git push origin main
```

For detailed AWS deployment instructions, see [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)

## 🔒 Security Best Practices

1. **Change default passwords** in production
2. **Use HTTPS** with valid SSL certificates
3. **Configure firewall** to restrict access
4. **Regular security updates** for dependencies
5. **Monitor logs** for suspicious activity
6. **Backup database** regularly
7. **Use environment variables** for secrets

## 📈 Performance Optimization

1. **Redis caching** for AI responses
2. **Database indexing** on frequently queried fields
3. **Nginx compression** for static assets
4. **Connection pooling** for database
5. **Worker process scaling** based on load

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql
# Check connection string in .env
```

**Redis Connection Error**
```bash
# Check Redis status
sudo systemctl status redis
# Test connection: redis-cli ping
```

**High Memory Usage**
```bash
# Restart workers periodically
# Monitor with: docker stats
# Adjust worker count in gunicorn.conf.py
```

## 📝 API Documentation

### Chat Endpoint
```bash
POST /chat
Content-Type: application/json

{
  "message": "Your question here"
}
```

### Admin Login
```bash
POST /admin/login
Content-Type: application/json

{
  "username": "admin",
  "password": "your_password"
}
```

### Analytics (Requires Auth)
```bash
GET /admin/analytics
Authorization: Bearer <jwt_token>
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Run security scans
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For production support:
- Check logs: `docker-compose logs web`
- Monitor metrics: `http://localhost:9090`
- Health status: `http://localhost:5000/health`
- Error tracking: Sentry dashboard
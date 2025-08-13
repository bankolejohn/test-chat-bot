import time
import structlog
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from flask import request, g
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
CHAT_REQUESTS = Counter('chat_requests_total', 'Total chat requests', ['sentiment'])
ACTIVE_SESSIONS = Gauge('active_sessions', 'Number of active chat sessions')
AI_RESPONSE_TIME = Histogram('ai_response_time_seconds', 'AI response time')

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def init_monitoring(app):
    """Initialize monitoring and logging"""
    if app.config.get('SENTRY_DSN'):
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.1,
            environment=app.config.get('FLASK_ENV', 'production')
        )

def before_request():
    """Track request start time"""
    g.start_time = time.time()
    g.request_id = f"{int(time.time())}-{id(request)}"

def after_request(response):
    """Log request metrics"""
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        REQUEST_DURATION.observe(duration)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.endpoint or 'unknown',
            status=response.status_code
        ).inc()
        
        logger.info(
            "request_completed",
            method=request.method,
            endpoint=request.endpoint,
            status_code=response.status_code,
            duration=duration,
            request_id=getattr(g, 'request_id', 'unknown')
        )
    
    return response

def log_chat_interaction(sentiment, response_time):
    """Log chat-specific metrics"""
    CHAT_REQUESTS.labels(sentiment=sentiment).inc()
    AI_RESPONSE_TIME.observe(response_time)

def get_metrics():
    """Get Prometheus metrics"""
    return generate_latest()
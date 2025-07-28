#!/usr/bin/env python3
"""
Monitoring and observability for 3MTT Chatbot
"""

import logging
import time
import json
from datetime import datetime
from flask import request, g
from functools import wraps
import os

class ChatbotMonitoring:
    """Monitoring and logging for the chatbot"""
    
    def __init__(self, app):
        self.app = app
        self.setup_logging()
        self.setup_metrics()
        self.setup_request_tracking()
    
    def setup_logging(self):
        """Setup structured logging"""
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(name)s %(message)s',
            handlers=[
                logging.FileHandler('logs/app.log'),
                logging.StreamHandler()
            ]
        )
        
        # Create specialized loggers
        self.app_logger = logging.getLogger('chatbot.app')
        self.security_logger = logging.getLogger('chatbot.security')
        self.performance_logger = logging.getLogger('chatbot.performance')
        self.ai_logger = logging.getLogger('chatbot.ai')
    
    def setup_metrics(self):
        """Setup metrics collection"""
        self.metrics = {
            'requests_total': 0,
            'requests_by_endpoint': {},
            'response_times': [],
            'errors_total': 0,
            'ai_requests': 0,
            'ai_failures': 0,
            'knowledge_base_hits': 0
        }
    
    def setup_request_tracking(self):
        """Setup request tracking middleware"""
        @self.app.before_request
        def before_request():
            g.start_time = time.time()
            g.request_id = f"{int(time.time())}-{id(request)}"
            
            self.app_logger.info(
                "Request started",
                extra={
                    'request_id': g.request_id,
                    'method': request.method,
                    'endpoint': request.endpoint,
                    'remote_addr': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', '')
                }
            )
        
        @self.app.after_request
        def after_request(response):
            if hasattr(g, 'start_time'):
                response_time = time.time() - g.start_time
                
                # Update metrics
                self.metrics['requests_total'] += 1
                endpoint = request.endpoint or 'unknown'
                self.metrics['requests_by_endpoint'][endpoint] = \
                    self.metrics['requests_by_endpoint'].get(endpoint, 0) + 1
                self.metrics['response_times'].append(response_time)
                
                if response.status_code >= 400:
                    self.metrics['errors_total'] += 1
                
                # Log response
                self.app_logger.info(
                    "Request completed",
                    extra={
                        'request_id': getattr(g, 'request_id', 'unknown'),
                        'status_code': response.status_code,
                        'response_time': response_time,
                        'content_length': response.content_length
                    }
                )
            
            return response
    
    def log_ai_request(self, message, response, response_time, success=True):
        """Log AI API requests"""
        self.metrics['ai_requests'] += 1
        if not success:
            self.metrics['ai_failures'] += 1
        
        self.ai_logger.info(
            "AI request",
            extra={
                'request_id': getattr(g, 'request_id', 'unknown'),
                'message_length': len(message),
                'response_length': len(response) if response else 0,
                'response_time': response_time,
                'success': success,
                'ai_model': os.getenv('AI_MODEL', 'unknown')
            }
        )
    
    def log_knowledge_base_search(self, query, results_count):
        """Log knowledge base searches"""
        self.metrics['knowledge_base_hits'] += 1
        
        self.app_logger.info(
            "Knowledge base search",
            extra={
                'request_id': getattr(g, 'request_id', 'unknown'),
                'query': query[:100],  # Truncate for privacy
                'results_count': results_count
            }
        )
    
    def log_security_event(self, event_type, details):
        """Log security events"""
        self.security_logger.warning(
            f"Security event: {event_type}",
            extra={
                'request_id': getattr(g, 'request_id', 'unknown'),
                'event_type': event_type,
                'details': details,
                'remote_addr': request.remote_addr if request else 'unknown',
                'user_agent': request.headers.get('User-Agent', '') if request else ''
            }
        )
    
    def get_metrics(self):
        """Get current metrics"""
        # Calculate averages
        avg_response_time = sum(self.metrics['response_times']) / len(self.metrics['response_times']) \
            if self.metrics['response_times'] else 0
        
        return {
            **self.metrics,
            'avg_response_time': avg_response_time,
            'error_rate': self.metrics['errors_total'] / max(self.metrics['requests_total'], 1),
            'ai_success_rate': (self.metrics['ai_requests'] - self.metrics['ai_failures']) / 
                              max(self.metrics['ai_requests'], 1),
            'timestamp': datetime.now().isoformat()
        }
    
    def health_check(self):
        """Perform health check"""
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        # Check knowledge base
        try:
            with open('knowledge_base.json', 'r') as f:
                json.load(f)
            health_status['checks']['knowledge_base'] = 'healthy'
        except Exception as e:
            health_status['checks']['knowledge_base'] = f'unhealthy: {str(e)}'
            health_status['status'] = 'degraded'
        
        # Check AI service (if configured)
        if os.getenv('OPENAI_API_KEY'):
            try:
                import openai
                # Simple test - don't actually call API to avoid costs
                health_status['checks']['ai_service'] = 'configured'
            except ImportError:
                health_status['checks']['ai_service'] = 'unavailable'
                health_status['status'] = 'degraded'
        else:
            health_status['checks']['ai_service'] = 'not_configured'
        
        # Check disk space
        import shutil
        disk_usage = shutil.disk_usage('.')
        free_space_gb = disk_usage.free / (1024**3)
        if free_space_gb < 1:  # Less than 1GB free
            health_status['checks']['disk_space'] = f'low: {free_space_gb:.2f}GB'
            health_status['status'] = 'degraded'
        else:
            health_status['checks']['disk_space'] = f'healthy: {free_space_gb:.2f}GB'
        
        return health_status

def monitor_function(func_name):
    """Decorator to monitor function performance"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            logger = logging.getLogger(f'chatbot.{func_name}')
            
            try:
                result = f(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.info(
                    f"Function {func_name} completed",
                    extra={
                        'function': func_name,
                        'execution_time': execution_time,
                        'success': True
                    }
                )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                
                logger.error(
                    f"Function {func_name} failed",
                    extra={
                        'function': func_name,
                        'execution_time': execution_time,
                        'error': str(e),
                        'success': False
                    }
                )
                raise
        
        return decorated_function
    return decorator

# Usage example:
# from monitoring import ChatbotMonitoring, monitor_function
# monitoring = ChatbotMonitoring(app)
# 
# @monitor_function('ai_response')
# def get_ai_response(message):
#     # Your function code here
#     pass
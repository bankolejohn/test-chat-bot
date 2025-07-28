#!/usr/bin/env python3
"""
Security middleware for 3MTT Chatbot
"""

from flask import request, jsonify, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import time
import re
import html

class SecurityMiddleware:
    """Security middleware for the Flask app"""
    
    def __init__(self, app):
        self.app = app
        self.setup_rate_limiting()
        self.setup_security_headers()
        self.setup_input_validation()
    
    def setup_rate_limiting(self):
        """Setup rate limiting"""
        self.limiter = Limiter(
            self.app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour", "10 per minute"]
        )
        
        # Apply rate limiting to chat endpoint
        self.limiter.limit("5 per minute")(self.app.view_functions['chat'])
    
    def setup_security_headers(self):
        """Add security headers to all responses"""
        @self.app.after_request
        def add_security_headers(response):
            # Prevent XSS
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            # HTTPS enforcement (in production)
            if not self.app.config.get('TESTING'):
                response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            # Content Security Policy
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "connect-src 'self'"
            )
            
            return response
    
    def setup_input_validation(self):
        """Setup input validation"""
        @self.app.before_request
        def validate_input():
            if request.endpoint == 'chat' and request.method == 'POST':
                # Check content length
                if request.content_length and request.content_length > 10000:  # 10KB limit
                    return jsonify({'error': 'Request too large'}), 413
                
                # Validate JSON structure
                try:
                    data = request.get_json()
                    if not data:
                        return jsonify({'error': 'Invalid JSON'}), 400
                    
                    message = data.get('message', '')
                    
                    # Message length validation
                    if len(message) > 1000:  # 1KB message limit
                        return jsonify({'error': 'Message too long'}), 400
                    
                    # Basic XSS prevention
                    if self.contains_malicious_content(message):
                        return jsonify({'error': 'Invalid content detected'}), 400
                    
                    # Store sanitized message
                    g.sanitized_message = html.escape(message)
                    
                except Exception:
                    return jsonify({'error': 'Invalid request format'}), 400
    
    def contains_malicious_content(self, text):
        """Check for potentially malicious content"""
        malicious_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',                # JavaScript URLs
            r'on\w+\s*=',                 # Event handlers
            r'<iframe[^>]*>',             # Iframes
            r'<object[^>]*>',             # Objects
            r'<embed[^>]*>',              # Embeds
        ]
        
        text_lower = text.lower()
        for pattern in malicious_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False

def require_api_key(f):
    """Decorator to require API key for admin endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        expected_key = os.getenv('ADMIN_API_KEY')
        
        if expected_key and api_key != expected_key:
            return jsonify({'error': 'Unauthorized'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def log_security_event(event_type, details):
    """Log security events"""
    import logging
    security_logger = logging.getLogger('security')
    security_logger.warning(f"Security Event: {event_type} - {details}")

# Usage example:
# from security_middleware import SecurityMiddleware, require_api_key
# security = SecurityMiddleware(app)
# 
# @app.route('/admin/sensitive')
# @require_api_key
# def sensitive_endpoint():
#     return jsonify({'data': 'sensitive'})
#!/usr/bin/env python3
"""
AWS Elastic Beanstalk entry point for 3MTT Chatbot
"""

import os
from app import create_app

# Create Flask application
application = create_app('production')

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
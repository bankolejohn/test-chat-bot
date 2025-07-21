import json
import os
from app import app
from werkzeug.serving import WSGIRequestHandler

# For AWS Lambda deployment
def lambda_handler(event, context):
    """AWS Lambda handler for the Flask app"""
    try:
        # Import serverless-wsgi for Lambda
        import serverless_wsgi
        return serverless_wsgi.handle_request(app, event, context)
    except ImportError:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'serverless-wsgi not installed. Run: pip install serverless-wsgi'
            })
        }

# For local testing
if __name__ == "__main__":
    app.run(debug=True)
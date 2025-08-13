import pytest
import json
from app import create_app
from models import db, Conversation, AdminUser
from auth import hash_password

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        # Create test admin user
        admin = AdminUser(
            username='testadmin',
            password_hash=hash_password('testpass'),
            email='test@example.com'
        )
        db.session.add(admin)
        db.session.commit()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_chat_endpoint(client):
    """Test chat functionality"""
    response = client.post('/chat', 
                          json={'message': 'Hello'},
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'response' in data

def test_chat_rate_limiting(client):
    """Test rate limiting on chat endpoint"""
    # Make multiple requests quickly
    for _ in range(15):  # Exceed rate limit
        client.post('/chat', json={'message': 'test'})
    
    response = client.post('/chat', json={'message': 'test'})
    assert response.status_code == 429

def test_admin_login(client):
    """Test admin login"""
    response = client.post('/admin/login',
                          json={'username': 'testadmin', 'password': 'testpass'},
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data

def test_invalid_login(client):
    """Test invalid admin login"""
    response = client.post('/admin/login',
                          json={'username': 'invalid', 'password': 'invalid'},
                          content_type='application/json')
    assert response.status_code == 401

def test_metrics_endpoint(client):
    """Test Prometheus metrics endpoint"""
    response = client.get('/metrics')
    assert response.status_code == 200
    assert 'text/plain' in response.content_type
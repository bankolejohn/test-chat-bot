#!/usr/bin/env python3
"""
Test suite for 3MTT Chatbot
"""

import pytest
import json
import os
from unittest.mock import patch, mock_open
from app import app, get_enhanced_mock_response, search_knowledge_base, load_knowledge_base

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_knowledge_base():
    """Sample knowledge base for testing"""
    return {
        "3mtt_program": {
            "overview": "Test program overview",
            "duration": "12 months"
        },
        "courses": {
            "available_tracks": ["Software Development", "Data Science"]
        }
    }

class TestChatEndpoint:
    """Test chat functionality"""
    
    def test_chat_valid_message(self, client):
        """Test chat with valid message"""
        response = client.post('/chat', 
                              json={'message': 'What is 3MTT?'})
        assert response.status_code == 200
        data = response.get_json()
        assert 'response' in data
        assert len(data['response']) > 0
    
    def test_chat_empty_message(self, client):
        """Test chat with empty message"""
        response = client.post('/chat', 
                              json={'message': ''})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_chat_no_message_field(self, client):
        """Test chat without message field"""
        response = client.post('/chat', json={})
        assert response.status_code == 400
    
    def test_chat_long_message(self, client):
        """Test chat with very long message"""
        long_message = "x" * 10000  # 10KB message
        response = client.post('/chat', 
                              json={'message': long_message})
        # Should handle gracefully
        assert response.status_code in [200, 400]

class TestKnowledgeBase:
    """Test knowledge base functionality"""
    
    def test_load_knowledge_base(self, sample_knowledge_base):
        """Test loading knowledge base"""
        with patch('builtins.open', mock_open(read_data=json.dumps(sample_knowledge_base))):
            kb = load_knowledge_base()
            assert '3mtt_program' in kb
            assert kb['3mtt_program']['duration'] == '12 months'
    
    def test_search_knowledge_base(self, sample_knowledge_base):
        """Test knowledge base search"""
        results = search_knowledge_base("program", sample_knowledge_base)
        assert len(results) > 0
        assert any("program" in result.lower() for result in results)
    
    def test_search_knowledge_base_no_results(self, sample_knowledge_base):
        """Test knowledge base search with no results"""
        results = search_knowledge_base("nonexistent", sample_knowledge_base)
        assert len(results) == 0

class TestResponseGeneration:
    """Test response generation"""
    
    def test_enhanced_mock_response_dashboard(self):
        """Test dashboard-related response"""
        response = get_enhanced_mock_response("dashboard scores different")
        assert "sync" in response.lower()
        assert "darey" in response.lower()
    
    def test_enhanced_mock_response_courses(self):
        """Test course-related response"""
        response = get_enhanced_mock_response("what courses available")
        assert "tracks" in response.lower() or "courses" in response.lower()
    
    def test_enhanced_mock_response_unknown(self):
        """Test unknown query response"""
        response = get_enhanced_mock_response("random unknown query xyz")
        assert len(response) > 0  # Should return default response

class TestAdminEndpoints:
    """Test admin functionality"""
    
    def test_analytics_endpoint(self, client):
        """Test analytics endpoint"""
        response = client.get('/admin/analytics')
        assert response.status_code == 200
        assert b'3MTT Chatbot Analytics' in response.data
    
    def test_knowledge_management_get(self, client):
        """Test knowledge management GET"""
        response = client.get('/admin/knowledge')
        assert response.status_code == 200
        assert b'Knowledge Base Management' in response.data

class TestSecurity:
    """Test security measures"""
    
    def test_xss_prevention(self, client):
        """Test XSS prevention"""
        malicious_input = "<script>alert('xss')</script>"
        response = client.post('/chat', 
                              json={'message': malicious_input})
        assert response.status_code == 200
        # Response should not contain unescaped script tags
        data = response.get_json()
        assert '<script>' not in data['response']
    
    def test_sql_injection_prevention(self, client):
        """Test SQL injection prevention (not applicable but good practice)"""
        malicious_input = "'; DROP TABLE users; --"
        response = client.post('/chat', 
                              json={'message': malicious_input})
        assert response.status_code == 200
        # Should handle gracefully without errors

class TestErrorHandling:
    """Test error handling"""
    
    @patch('app.get_ai_response')
    def test_ai_failure_fallback(self, mock_ai, client):
        """Test fallback when AI fails"""
        mock_ai.side_effect = Exception("AI service down")
        response = client.post('/chat', 
                              json={'message': 'test message'})
        assert response.status_code == 200
        # Should fall back to mock response
    
    @patch('builtins.open')
    def test_knowledge_base_file_missing(self, mock_open_func, client):
        """Test behavior when knowledge base file is missing"""
        mock_open_func.side_effect = FileNotFoundError()
        response = client.post('/chat', 
                              json={'message': 'test message'})
        assert response.status_code == 200
        # Should handle gracefully

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
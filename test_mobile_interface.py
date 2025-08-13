#!/usr/bin/env python3
"""
Test script to verify mobile-friendly interface
"""

from app import app

def test_mobile_interface():
    """Test the mobile-friendly interface"""
    print("🔍 Testing Mobile-Friendly Interface")
    print("=" * 50)
    
    with app.test_client() as client:
        # Test main chat interface
        print("\n1. Testing Main Chat Interface...")
        response = client.get('/')
        assert response.status_code == 200
        
        # Check for mobile viewport meta tag
        html_content = response.data.decode('utf-8')
        assert 'viewport' in html_content
        assert 'width=device-width' in html_content
        print("✅ Mobile viewport meta tag present")
        
        # Check for responsive CSS
        assert '@media' in html_content
        assert 'max-width: 768px' in html_content
        print("✅ Mobile CSS media queries present")
        
        # Check for mobile-friendly elements
        assert 'chat-container' in html_content
        assert 'message-avatar' in html_content
        print("✅ Mobile-friendly chat elements present")
        
        # Test analytics page
        print("\n2. Testing Analytics Interface...")
        response = client.get('/admin/analytics')
        assert response.status_code == 200
        
        analytics_content = response.data.decode('utf-8')
        assert 'viewport' in analytics_content
        assert 'metrics-grid' in analytics_content
        print("✅ Mobile-friendly analytics interface")
        
        # Test knowledge base management
        print("\n3. Testing Knowledge Base Interface...")
        response = client.get('/admin/knowledge')
        assert response.status_code == 200
        
        kb_content = response.data.decode('utf-8')
        assert 'viewport' in kb_content
        assert 'knowledge-editor' in kb_content
        print("✅ Mobile-friendly knowledge base interface")
        
        # Test health endpoint
        print("\n4. Testing Health Check...")
        response = client.get('/health')
        assert response.status_code == 200
        print("✅ Health check working")
        
        print("\n🎉 All mobile interface tests passed!")
        print("\n📱 Mobile Features Added:")
        print("   • Responsive design for all screen sizes")
        print("   • Touch-friendly buttons and inputs")
        print("   • Optimized chat interface with avatars")
        print("   • Mobile-friendly admin panels")
        print("   • Proper viewport configuration")
        print("   • CSS media queries for different devices")
        print("   • Auto-resizing text areas")
        print("   • Improved typography and spacing")

if __name__ == "__main__":
    test_mobile_interface()
"""
Unit Tests for GET /{shortCode} Redirect (TASK-2.2)
Run: pytest test_redirect.py -v
"""
import sys
import os
import pytest
import json
from app import app
from models import Link, get_session

@pytest.fixture
def client():
    """Create Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def setup_db():
    """Setup test data"""
    session = get_session()
    session.query(Link).delete()
    
    # Create test link
    test_link = Link(
        shortCode='test01',
        longUrl='https://www.example.com',
        clickCount=0,
        isActive=True
    )
    session.add(test_link)
    session.commit()
    
    yield session
    
    session.query(Link).delete()
    session.commit()
    session.close()

class TestRedirectEndpoint:
    """Tests for GET /{shortCode}"""
    
    def test_redirect_valid_short_code(self, client, setup_db):
        """Test redirect with valid short code"""
        response = client.get('/test01', follow_redirects=False)
        assert response.status_code == 302
        assert 'https://www.example.com' in response.location
    
    def test_redirect_increments_click_count(self, client, setup_db):
        """Test that redirect increments click counter"""
        # Get initial count
        session = get_session()
        link = session.query(Link).filter_by(shortCode='test01').first()
        initial_count = link.clickCount
        session.close()
        
        # Make redirect request
        client.get('/test01', follow_redirects=False)
        
        # Check count incremented
        session = get_session()
        link = session.query(Link).filter_by(shortCode='test01').first()
        assert link.clickCount == initial_count + 1
        session.close()
    
    def test_redirect_invalid_short_code(self, client, setup_db):
        """Test redirect with non-existent short code"""
        response = client.get('/invalid123', follow_redirects=False)
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'error' in data
    
    def test_redirect_inactive_link(self, client, setup_db):
        """Test redirect for deactivated link"""
        # Deactivate link
        session = get_session()
        link = session.query(Link).filter_by(shortCode='test01').first()
        link.isActive = False
        session.commit()
        session.close()
        
        # Try to redirect
        response = client.get('/test01', follow_redirects=False)
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'deactivated' in data.get('error', '').lower()

class TestAnalyticsLogging:
    """Tests for analytics logging during redirect"""
    
    def test_analytics_logged_on_redirect(self, client, setup_db):
        """Test that click analytics are logged"""
        from models import Analytics
        
        session = get_session()
        initial_count = session.query(Analytics).count()
        session.close()
        
        # Make request
        client.get('/test01', follow_redirects=False, 
                   headers={'User-Agent': 'TestAgent', 'Referer': 'http://test.com'})
        
        # Check analytics created
        session = get_session()
        analytics = session.query(Analytics).all()
        assert len(analytics) > initial_count
        session.close()

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

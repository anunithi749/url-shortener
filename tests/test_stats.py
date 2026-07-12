"""
Unit Tests for GET /stats/{shortCode} Analytics (TASK-2.3)
Run: pytest test_stats.py -v
"""
import os
import sys
import pytest
import json
from app import app
from models import Link, Analytics, get_session
from datetime import datetime

@pytest.fixture
def client():
    """Create Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def setup_db():
    """Setup test data with analytics"""
    session = get_session()
    session.query(Analytics).delete()
    session.query(Link).delete()
    
    # Create test link
    test_link = Link(
        shortCode='stat01',
        longUrl='https://www.example.com',
        clickCount=5,
        isActive=True
    )
    session.add(test_link)
    session.commit()
    
    # Add sample analytics
    for i in range(5):
        analytics = Analytics(
            linkId=test_link.id,
            timestamp=datetime.utcnow(),
            ipAddress=f'192.168.1.{i}',
            referrer='https://google.com' if i % 2 == 0 else 'Direct',
            userAgent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)' if i % 2 == 0 else 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
            geolocation='USA'
        )
        session.add(analytics)
    
    session.commit()
    yield session
    
    session.query(Analytics).delete()
    session.query(Link).delete()
    session.commit()
    session.close()

class TestStatsEndpoint:
    """Tests for GET /stats/{shortCode}"""
    
    def test_stats_valid_short_code(self, client, setup_db):
        """Test stats for valid short code"""
        response = client.get('/stats/stat01')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['shortCode'] == 'stat01'
    
    def test_stats_contains_required_fields(self, client, setup_db):
        """Test that stats response has all required fields"""
        response = client.get('/stats/stat01')
        data = json.loads(response.data)
        
        # Check required fields
        assert 'totalClicks' in data
        assert 'uniqueVisitors' in data
        assert 'topReferrers' in data
        assert 'deviceBreakdown' in data
        assert 'createdAt' in data
    
    def test_stats_click_count_matches(self, client, setup_db):
        """Test that total clicks matches database"""
        response = client.get('/stats/stat01')
        data = json.loads(response.data)
        
        # Should be 5 clicks from setup
        assert data['totalClicks'] == 5
    
    def test_stats_invalid_short_code(self, client, setup_db):
        """Test stats for non-existent short code"""
        response = client.get('/stats/invalid999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'error' in data
    
    def test_stats_device_breakdown(self, client, setup_db):
        """Test device breakdown calculation"""
        response = client.get('/stats/stat01')
        data = json.loads(response.data)
        
        # Should have device breakdown
        assert 'deviceBreakdown' in data
        breakdown = data['deviceBreakdown']
        assert 'mobile' in breakdown
        assert 'desktop' in breakdown
    
    def test_stats_top_referrers(self, client, setup_db):
        """Test top referrers list"""
        response = client.get('/stats/stat01')
        data = json.loads(response.data)
        
        # Should have top referrers
        assert 'topReferrers' in data
        assert isinstance(data['topReferrers'], list)
    
    def test_stats_empty_analytics(self, client):
        """Test stats with no click analytics"""
        session = get_session()
        session.query(Analytics).delete()
        session.query(Link).delete()
        
        # Create link with no analytics
        empty_link = Link(
            shortCode='empty1',
            longUrl='https://example.com',
            clickCount=0,
            isActive=True
        )
        session.add(empty_link)
        session.commit()
        session.close()
        
        response = client.get('/stats/empty1')
        data = json.loads(response.data)
        
        assert data['success'] == True
        assert data['totalClicks'] == 0
        assert data['uniqueVisitors'] == 0

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

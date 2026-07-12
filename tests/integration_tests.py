"""
Integration Tests for URL Shortener Service (TASK-3.1)
Tests complete user workflows end-to-end
Run: pytest integration_tests.py -v
"""

import sys
import os
import pytest
import json
from app import app
from models import Link, Analytics, get_session

@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def clean_db():
    """Clean database before each test"""
    session = get_session()
    session.query(Analytics).delete()
    session.query(Link).delete()
    session.commit()
    session.close()

class TestCompleteWorkflow:
    """Integration tests for complete workflows"""
    
    def test_workflow_shorten_visit_view_stats(self, client, clean_db):
        """Complete workflow: shorten URL → visit → view stats"""
        
        # Step 1: Shorten a URL
        shorten_response = client.post('/shorten',
            data=json.dumps({'longUrl': 'https://www.example.com/test'}),
            content_type='application/json'
        )
        assert shorten_response.status_code == 200
        shorten_data = json.loads(shorten_response.data)
        assert shorten_data['success'] == True
        short_code = shorten_data['shortCode']
        
        # Step 2: Visit the short URL (simulate 3 clicks)
        for i in range(3):
            redirect_response = client.get(f'/{short_code}', follow_redirects=False)
            assert redirect_response.status_code == 302
            assert redirect_response.location == 'https://www.example.com/test'
        
        # Step 3: View stats
        stats_response = client.get(f'/stats/{short_code}')
        assert stats_response.status_code == 200
        stats_data = json.loads(stats_response.data)
        
        # Verify stats
        assert stats_data['success'] == True
        assert stats_data['totalClicks'] == 3
        assert stats_data['shortCode'] == short_code
        assert stats_data['longUrl'] == 'https://www.example.com/test'
    
    def test_workflow_multiple_urls(self, client, clean_db):
        """Test multiple URLs shortened and accessed"""
        
        urls = [
            'https://www.google.com',
            'https://www.github.com',
            'https://www.stackoverflow.com'
        ]
        short_codes = []
        
        # Shorten all URLs
        for url in urls:
            response = client.post('/shorten',
                data=json.dumps({'longUrl': url}),
                content_type='application/json'
            )
            data = json.loads(response.data)
            assert data['success'] == True
            short_codes.append(data['shortCode'])
        
        # Verify all are different
        assert len(set(short_codes)) == len(short_codes)
        
        # Access each URL
        for short_code, expected_url in zip(short_codes, urls):
            response = client.get(f'/{short_code}', follow_redirects=False)
            assert response.status_code == 302
            assert response.location == expected_url

class TestRateLimitingIntegration:
    """Test rate limiting across requests"""
    
    def test_rate_limiting_blocks_excess_requests(self, client, clean_db):
        """Verify rate limiting works"""
        
        # Make 101 requests (limit is 100)
        responses = []
        for i in range(105):
            response = client.get('/', headers={'X-Forwarded-For': '192.168.1.1'})
            responses.append(response.status_code)
        
        # Most should succeed (200)
        success_count = responses.count(200)
        assert success_count >= 100
        
        # Some should be rate limited (429)
        rate_limited = responses.count(429)
        assert rate_limited > 0

class TestErrorHandling:
    """Test error handling workflows"""
    
    def test_error_flow_invalid_then_valid(self, client, clean_db):
        """Test recovery from error"""
        
        # Send invalid request
        bad_response = client.post('/shorten',
            data=json.dumps({'longUrl': 'not-a-url'}),
            content_type='application/json'
        )
        assert bad_response.status_code == 400
        
        # Send valid request (should work)
        good_response = client.post('/shorten',
            data=json.dumps({'longUrl': 'https://example.com'}),
            content_type='application/json'
        )
        assert good_response.status_code == 200
        data = json.loads(good_response.data)
        assert data['success'] == True

class TestDataPersistence:
    """Test data is persisted correctly"""
    
    def test_data_persists_across_requests(self, client, clean_db):
        """Verify data saved in DB persists"""
        
        # Create a shortened URL
        response1 = client.post('/shorten',
            data=json.dumps({'longUrl': 'https://persistent.example.com'}),
            content_type='application/json'
        )
        data1 = json.loads(response1.data)
        short_code = data1['shortCode']
        
        # Check database directly
        session = get_session()
        link = session.query(Link).filter_by(shortCode=short_code).first()
        assert link is not None
        assert link.longUrl == 'https://persistent.example.com'
        
        # Verify via API
        response2 = client.get(f'/stats/{short_code}')
        data2 = json.loads(response2.data)
        assert data2['longUrl'] == 'https://persistent.example.com'
        session.close()

class TestConcurrentOperations:
    """Test concurrent-like operations"""
    
    def test_shorten_then_immediate_stats(self, client, clean_db):
        """Shorten URL and immediately get stats"""
        
        response1 = client.post('/shorten',
            data=json.dumps({'longUrl': 'https://concurrent.example.com'}),
            content_type='application/json'
        )
        data1 = json.loads(response1.data)
        short_code = data1['shortCode']
        
        # Immediately get stats
        response2 = client.get(f'/stats/{short_code}')
        data2 = json.loads(response2.data)
        
        assert data2['success'] == True
        assert data2['shortCode'] == short_code
        assert data2['totalClicks'] == 0  # No clicks yet

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

"""
Unit Tests for POST /shorten Endpoint (TASK-2.1)
Run: pytest test_shorten.py -v
"""
import sys
import os
import pytest
import json
import os
from app import app
from models import Link, get_session

@pytest.fixture
def client():
    """Create Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def clear_db():
    """Clear database before each test"""
    session = get_session()
    session.query(Link).delete()
    session.commit()
    session.close()

class TestShortenEndpoint:
    """Tests for POST /shorten"""
    
    def test_shorten_valid_url(self, client, clear_db):
        """Test shortening a valid URL"""
        response = client.post('/shorten', 
            data=json.dumps({'longUrl': 'https://www.example.com'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'shortCode' in data
        assert 'shortUrl' in data
    
    def test_shorten_missing_long_url(self, client, clear_db):
        """Test with missing longUrl field"""
        response = client.post('/shorten',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'error' in data
    
    def test_shorten_invalid_url_format(self, client, clear_db):
        """Test with invalid URL (no protocol)"""
        response = client.post('/shorten',
            data=json.dumps({'longUrl': 'example.com'}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'error' in data
    
    def test_shorten_url_too_long(self, client, clear_db):
        """Test with URL exceeding length limit"""
        long_url = 'https://example.com/' + 'a' * 2000
        response = client.post('/shorten',
            data=json.dumps({'longUrl': long_url}),
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_shorten_duplicate_url_idempotent(self, client, clear_db):
        """Test that duplicate URLs return same shortCode (idempotency)"""
        url = 'https://www.example.com/test'
        
        # First request
        response1 = client.post('/shorten',
            data=json.dumps({'longUrl': url}),
            content_type='application/json'
        )
        data1 = json.loads(response1.data)
        short_code_1 = data1['shortCode']
        
        # Second request with same URL
        response2 = client.post('/shorten',
            data=json.dumps({'longUrl': url}),
            content_type='application/json'
        )
        data2 = json.loads(response2.data)
        short_code_2 = data2['shortCode']
        
        # Should return same short code
        assert short_code_1 == short_code_2
        assert data2['message'] == 'URL already shortened (idempotent)'
    
    def test_shorten_wrong_content_type(self, client, clear_db):
        """Test with wrong Content-Type header"""
        response = client.post('/shorten',
            data='longUrl=https://example.com',
            content_type='application/x-www-form-urlencoded'
        )
        assert response.status_code == 400
    
    def test_shorten_short_code_format(self, client, clear_db):
        """Test that shortCode has correct format"""
        response = client.post('/shorten',
            data=json.dumps({'longUrl': 'https://www.example.com'}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        short_code = data['shortCode']
        
        # Should be 6 characters
        assert len(short_code) == 6
        # Should be alphanumeric
        assert short_code.isalnum()

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

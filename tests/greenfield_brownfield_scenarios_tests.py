"""
Greenfield & Brownfield Scenario Tests (TASK-2.7)
Tests explicit scenario coverage from Day 1 requirements
Run: pytest greenfield_brownfield_scenarios_tests.py -v
"""

import os
import sys
# ✅ FIX: Add src/ to path so imports work in pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

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

# =====================================================================
# GREENFIELD SCENARIOS - Fresh System Deployment
# =====================================================================

class TestGreenfield:
    """Tests for fresh system deployment (no pre-existing data)"""
    
    def test_gf1_fresh_deployment_empty_database(self, client, clean_db):
        """
        GF-1: Fresh Deployment - System starts with empty database
        
        Requirement: System should handle initial deployment to clean environment
        Validates: Database initialization, empty state handling
        """
        # Verify database is empty
        session = get_session()
        link_count = session.query(Link).count()
        analytics_count = session.query(Analytics).count()
        session.close()
        
        assert link_count == 0, "Database should be empty on fresh deployment"
        assert analytics_count == 0, "Analytics table should be empty"
        
        # Verify API responds correctly to stats request on non-existent URL
        response = client.get('/stats/nonexistent')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] == False
    
    def test_gf2_first_url_creation_generates_correct_code(self, client, clean_db):
        """
        GF-2: First URL Creation - First shortened URL gets correct short code
        
        Requirement: First URL in fresh system should get predictable short code
        Validates: Short code generation starts from expected value
        """
        # Create first URL in empty system
        response = client.post('/shorten',
            data=json.dumps({'longUrl': 'https://example.com/first'}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        
        # First URL should generate predictable short code
        first_short_code = data['shortCode']
        assert first_short_code == '000001', f"First URL should have code 000001, got {first_short_code}"
        
        # Verify second URL gets next code
        response2 = client.post('/shorten',
            data=json.dumps({'longUrl': 'https://example.com/second'}),
            content_type='application/json'
        )
        data2 = json.loads(response2.data)
        second_short_code = data2['shortCode']
        assert second_short_code == '000002', f"Second URL should have code 000002, got {second_short_code}"
    
    def test_gf3_multiple_urls_rapid_succession_no_conflicts(self, client, clean_db):
        """
        GF-3: Multiple URLs Rapid Succession - No conflicts or race conditions
        
        Requirement: System should handle rapid URL creation without conflicts
        Validates: Sequential code generation, no duplicates, no collisions
        """
        urls = [
            'https://example.com/1',
            'https://example.com/2',
            'https://example.com/3',
            'https://example.com/4',
            'https://example.com/5',
        ]
        
        short_codes = []
        
        # Create multiple URLs rapidly
        for url in urls:
            response = client.post('/shorten',
                data=json.dumps({'longUrl': url}),
                content_type='application/json'
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            short_codes.append(data['shortCode'])
        
        # Verify all codes are unique
        assert len(set(short_codes)) == len(short_codes), "All short codes should be unique"
        
        # Verify codes are sequential
        expected_codes = ['000001', '000002', '000003', '000004', '000005']
        assert short_codes == expected_codes, f"Codes should be sequential, got {short_codes}"
        
        # Verify all can be accessed
        for short_code in short_codes:
            response = client.get(f'/{short_code}', follow_redirects=False)
            assert response.status_code == 302, f"Code {short_code} should redirect"

# =====================================================================
# BROWNFIELD SCENARIOS - Running System with Existing Data
# =====================================================================

class TestBrownfield:
    """Tests for running system with pre-existing data"""
    
    def test_bf1_existing_urls_already_in_system(self, client, clean_db):
        """
        BF-1: Existing URLs - System handles pre-populated data correctly
        
        Requirement: System should work with existing URLs in database
        Validates: Querying, redirecting, and stats on pre-existing data
        """
        # Pre-populate database with existing links
        session = get_session()
        existing_links = [
            Link(shortCode='old01', longUrl='https://existing.com/1', clickCount=10, isActive=True),
            Link(shortCode='old02', longUrl='https://existing.com/2', clickCount=25, isActive=True),
        ]
        for link in existing_links:
            session.add(link)
        session.commit()
        session.close()
        
        # System should handle existing URLs seamlessly
        # Test 1: Can redirect to existing URL
        response = client.get('/old01', follow_redirects=False)
        assert response.status_code == 302
        assert response.location == 'https://existing.com/1'
        
        # Test 2: Can get stats on existing URL
        response = client.get('/stats/old01')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['totalClicks'] == 10
        
        # Test 3: New URL creation works alongside existing URLs
        response = client.post('/shorten',
            data=json.dumps({'longUrl': 'https://new.com/url'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        # New code should not conflict with existing
        assert data['shortCode'] not in ['old01', 'old02']
    
    def test_bf2_duplicate_url_idempotency_brownfield(self, client, clean_db):
        """
        BF-2: Duplicate URL Submissions - Idempotency in running system
        
        Requirement: Duplicate URLs should return same code (idempotent)
        Validates: Prevents duplicate URLs in active system
        
        SCENARIO COVERAGE: Extends test_shorten_duplicate_url_idempotent to brownfield context
        """
        # Pre-populate with existing URL
        session = get_session()
        existing = Link(shortCode='exists', longUrl='https://dup.com/test', clickCount=5, isActive=True)
        session.add(existing)
        session.commit()
        session.close()
        
        # Try to shorten the SAME URL that already exists
        response = client.post('/shorten',
            data=json.dumps({'longUrl': 'https://dup.com/test'}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['shortCode'] == 'exists', "Should return existing short code (idempotent)"
        assert 'message' in data
        assert 'idempotent' in data['message'].lower()
    
    def test_bf3_rate_limiting_on_active_system(self, client, clean_db):
        """
        BF-3: Rate Limiting on Active System - Enforced on running system
        
        Requirement: Rate limiting should work on active system with existing traffic
        Validates: Rate limit enforcement doesn't break with data
        
        SCENARIO COVERAGE: Extends test_rate_limiting_blocks_excess_requests to brownfield
        """
        # Pre-populate database
        session = get_session()
        for i in range(5):
            link = Link(shortCode=f'link{i:02d}', longUrl=f'https://existing.com/{i}', clickCount=i*10, isActive=True)
            session.add(link)
        session.commit()
        session.close()
        
        # Now apply rate limiting on running system
        test_ip = '192.168.1.100'
        response_codes = []
        
        for i in range(105):
            response = client.get('/', headers={'X-Forwarded-For': test_ip})
            response_codes.append(response.status_code)
        
        # Should have 429s despite existing data
        assert 429 in response_codes, "Rate limiting should trigger on active system"
        
        # Most requests should succeed (first 100)
        success_count = response_codes.count(200)
        assert success_count >= 100, f"First 100 requests should succeed, got {success_count}"
        
        # Some should be rate limited
        limited_count = response_codes.count(429)
        assert limited_count > 0, f"Excess requests should be rate limited, got {limited_count} 429s"
    
    def test_bf4_system_recovery_after_errors(self, client, clean_db):
        """
        BF-4: System Recovery After Errors - Graceful recovery in running system
        
        Requirement: System should recover from errors and continue operating
        Validates: Error handling doesn't corrupt system state
        
        SCENARIO COVERAGE: Extends test_error_flow_invalid_then_valid to brownfield
        """
        # Pre-populate with existing valid data
        session = get_session()
        existing = Link(shortCode='valid', longUrl='https://valid.com/url', clickCount=3, isActive=True)
        session.add(existing)
        session.commit()
        session.close()
        
        # Verify existing data works
        response = client.get('/stats/valid')
        assert response.status_code == 200
        
        # Send invalid request (should error)
        response = client.post('/shorten',
            data=json.dumps({'longUrl': 'not-a-valid-url'}),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # System should recover - existing data still accessible
        response = client.get('/stats/valid')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['totalClicks'] == 3, "Existing data should not be corrupted"
        
        # New valid request should work
        response = client.post('/shorten',
            data=json.dumps({'longUrl': 'https://newafter.error.com'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True, "System should recover after error"

# =====================================================================
# COMBINED SCENARIOS - Transitioning Between Greenfield & Brownfield
# =====================================================================

class TestScenarioTransitions:
    """Tests for transitions between greenfield and brownfield states"""
    
    def test_greenfield_to_brownfield_transition(self, client, clean_db):
        """
        Test transition from fresh deployment (greenfield) to running system (brownfield)
        
        Flow: Empty DB → Create URLs → System running → Add more URLs → Verify no conflicts
        """
        # GREENFIELD: Start with empty system
        response = client.get('/stats/anycode')
        assert response.status_code == 404
        
        # Create first batch of URLs (greenfield)
        codes_batch1 = []
        for i in range(3):
            response = client.post('/shorten',
                data=json.dumps({'longUrl': f'https://batch1.com/{i}'}),
                content_type='application/json'
            )
            data = json.loads(response.data)
            codes_batch1.append(data['shortCode'])
        
        # BROWNFIELD: System now has data
        session = get_session()
        count = session.query(Link).count()
        session.close()
        assert count == 3, "Should have 3 links in brownfield state"
        
        # Add more URLs (brownfield operations)
        codes_batch2 = []
        for i in range(3):
            response = client.post('/shorten',
                data=json.dumps({'longUrl': f'https://batch2.com/{i}'}),
                content_type='application/json'
            )
            data = json.loads(response.data)
            codes_batch2.append(data['shortCode'])
        
        # Verify no conflicts between batches
        all_codes = codes_batch1 + codes_batch2
        assert len(set(all_codes)) == len(all_codes), "All codes should be unique"
        
        # Verify all can be accessed
        for code in all_codes:
            response = client.get(f'/{code}', follow_redirects=False)
            assert response.status_code == 302, f"Code {code} should work in brownfield"

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

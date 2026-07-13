"""
Greenfield & Brownfield Scenario Tests (TASK-3.6)
Tests explicit scenario coverage from Day 1 requirements
Run: pytest tests/greenfield_brownfield_scenarios_tests.py -v
"""

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
    from rate_limiter import rate_limiter  # ✅ FIX: Use correct name
    
    session = get_session()
    session.query(Analytics).delete()
    session.query(Link).delete()
    session.commit()
    session.close()
    
    # ✅ CRITICAL: Reset rate limiter for each test
    rate_limiter.requests.clear()

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
        session = get_session()
        link_count = session.query(Link).count()
        session.close()
        
        assert link_count == 0, "Database should be empty on fresh deployment"
    
    def test_gf2_first_url_creation_generates_correct_code(self, client, clean_db):
        """
        GF-2: First URL Creation - Generate unique short code
        
        Requirement: First URL submission should generate valid short code
        Validates: Code generation, URL storage, response format
        """
        response = client.post('/shorten',
            data=json.dumps({'longUrl': 'https://example.com/first'}),
            content_type='application/json'
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = json.loads(response.data)
        assert data['success'] == True, "Should succeed"
        assert 'shortCode' in data, "Response should contain shortCode"
        
        session = get_session()
        link_count = session.query(Link).count()
        session.close()
        
        assert link_count == 1, "URL should be stored in database"
    
    def test_gf3_multiple_urls_rapid_succession_no_conflicts(self, client, clean_db):
        """
        GF-3: Multiple URLs Rapid Creation - No collisions
        
        Requirement: Concurrent submissions should not create duplicate codes
        Validates: Collision-free generation, atomicity
        """
        urls = [
            'https://example.com/1',
            'https://example.com/2',
            'https://example.com/3',
        ]
        
        short_codes = []
        
        for url in urls:
            response = client.post('/shorten',
                data=json.dumps({'longUrl': url}),
                content_type='application/json'
            )
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = json.loads(response.data)
            assert data['success'] == True
            short_codes.append(data['shortCode'])
        
        assert len(set(short_codes)) == len(short_codes), "All short codes should be unique"
        
        session = get_session()
        link_count = session.query(Link).count()
        session.close()
        
        assert link_count == 3, f"All 3 URLs should be stored, got {link_count}"

# =====================================================================
# BROWNFIELD SCENARIOS - Running System with Existing Data
# =====================================================================

class TestBrownfield:
    """Tests for running system with pre-existing data"""
    
    def test_bf1_existing_urls_already_in_system(self, client, clean_db):
        """
        BF-1: Existing URLs - System handles pre-populated data correctly
        
        Requirement: System should work with existing URLs in database
        Validates: Querying, redirecting on pre-existing data
        """
        session = get_session()
        link1 = Link(shortCode='old01', longUrl='https://existing.com/1', clickCount=10, isActive=True)
        link2 = Link(shortCode='old02', longUrl='https://existing.com/2', clickCount=25, isActive=True)
        session.add(link1)
        session.add(link2)
        session.commit()
        
        count = session.query(Link).count()
        session.close()
        
        assert count == 2, f"Expected 2 links, got {count}"
        
        response = client.get('/old01', follow_redirects=False)
        assert response.status_code == 302, f"Expected redirect (302), got {response.status_code}"
        assert response.location == 'https://existing.com/1', "Should redirect to correct URL"
    
    def test_bf2_duplicate_url_idempotency_brownfield(self, client, clean_db):
        """
        BF-2: Duplicate URL Submissions - Idempotency in running system
        
        Requirement: Duplicate URLs should return same code (idempotent)
        Validates: Prevents duplicate URLs in active system
        """
        url = 'https://dup.com/test'
        
        response1 = client.post('/shorten',
            data=json.dumps({'longUrl': url}),
            content_type='application/json'
        )
        assert response1.status_code == 200
        data1 = json.loads(response1.data)
        code1 = data1['shortCode']
        
        response2 = client.post('/shorten',
            data=json.dumps({'longUrl': url}),
            content_type='application/json'
        )
        assert response2.status_code == 200
        data2 = json.loads(response2.data)
        code2 = data2['shortCode']
        
        assert code1 == code2, f"Duplicate URL should return same code: {code1} != {code2}"
        
        session = get_session()
        count = session.query(Link).filter_by(longUrl=url).count()
        session.close()
        
        assert count == 1, f"Should have only 1 entry for duplicate URL, got {count}"
    
    def test_bf3_rate_limiting_on_active_system(self, client, clean_db):
        """
        BF-3: Rate Limiting - Enforced on active system
        
        Requirement: Rate limiting should prevent abuse
        Validates: 429 response after limit exceeded
        """
        success_count = 0
        blocked_count = 0
        
        for i in range(101):
            response = client.post('/shorten',
                data=json.dumps({'longUrl': f'https://example.com/url{i}'}),
                content_type='application/json'
            )
            
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                blocked_count += 1
        
        assert success_count >= 100, f"Expected at least 100 successes, got {success_count}"
        assert blocked_count > 0, f"Expected rate limit blocks, got {blocked_count}"
    
    def test_bf4_system_recovery_after_errors(self, client, clean_db):
        """
        BF-4: Error Recovery - System recovers from errors
        
        Requirement: System should remain consistent after errors
        Validates: Transaction rollback, data integrity
        """
        response = client.post('/shorten',
            data=json.dumps({'longUrl': 'https://example.com/test'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data1 = json.loads(response.data)
        assert data1['success'] == True
        
        response = client.post('/shorten',
            data=json.dumps({'longUrl': 'invalid-url-no-protocol'}),
            content_type='application/json'
        )
        assert response.status_code == 400, "Invalid URL should return 400"
        
        response = client.post('/shorten',
            data=json.dumps({'longUrl': 'https://example.com/after-error'}),
            content_type='application/json'
        )
        assert response.status_code == 200, "System should recover after error"
        data2 = json.loads(response.data)
        assert data2['success'] == True
        
        session = get_session()
        count = session.query(Link).count()
        session.close()
        
        assert count == 2, f"Should have 2 valid URLs, got {count}"

class TestScenarioTransitions:
    """Tests for transitions between greenfield and brownfield"""
    
    def test_greenfield_to_brownfield_transition(self, client, clean_db):
        """
        Transition Test: System moves from greenfield to brownfield state
        
        Validates: Clean transition from empty to pre-populated state
        """
        session = get_session()
        initial_count = session.query(Link).count()
        session.close()
        
        assert initial_count == 0, "Should start empty"
        
        for i in range(3):
            response = client.post('/shorten',
                data=json.dumps({'longUrl': f'https://example.com/url{i}'}),
                content_type='application/json'
            )
            assert response.status_code == 200, f"Failed to create URL {i}"
        
        session = get_session()
        final_count = session.query(Link).count()
        session.close()
        
        assert final_count == 3, f"Should have 3 URLs after transition, got {final_count}"
        
        response = client.get('/1', follow_redirects=False)
        assert response.status_code in [302, 404], f"Should be redirect or not found, got {response.status_code}"

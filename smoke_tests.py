"""
Smoke Tests - Final Verification (TASK-3.5)
Quick tests to verify system is working end-to-end
Run: python smoke_tests.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_smoke_all():
    """Run all smoke tests"""
    print("\n" + "="*60)
    print("URL SHORTENER - SMOKE TESTS")
    print("="*60 + "\n")
    
    results = []
    
    # Test 1: Home endpoint
    print("Test 1: Home endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert data['service'] == 'URL Shortener API'
        print("  ✓ PASSED\n")
        results.append(True)
    except Exception as e:
        print(f"  ✗ FAILED: {str(e)}\n")
        results.append(False)
    
    # Test 2: Shorten URL
    print("Test 2: POST /shorten...")
    try:
        response = requests.post(
            f"{BASE_URL}/shorten",
            json={'longUrl': 'https://www.example.com/smoke-test'},
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'shortCode' in data
        short_code = data['shortCode']
        print(f"  ✓ PASSED - Short code: {short_code}\n")
        results.append(True)
    except Exception as e:
        print(f"  ✗ FAILED: {str(e)}\n")
        results.append(False)
        short_code = None
    
    if short_code:
        # Test 3: Redirect
        print("Test 3: GET /{shortCode} (redirect)...")
        try:
            response = requests.get(
                f"{BASE_URL}/{short_code}",
                allow_redirects=False
            )
            assert response.status_code == 302
            assert 'https://www.example.com' in response.headers.get('location', '')
            print("  ✓ PASSED\n")
            results.append(True)
        except Exception as e:
            print(f"  ✗ FAILED: {str(e)}\n")
            results.append(False)
        
        # Test 4: Stats
        print("Test 4: GET /stats/{shortCode}...")
        try:
            response = requests.get(f"{BASE_URL}/stats/{short_code}")
            assert response.status_code == 200
            data = response.json()
            assert data['success'] == True
            assert data['shortCode'] == short_code
            assert 'totalClicks' in data
            print("  ✓ PASSED\n")
            results.append(True)
        except Exception as e:
            print(f"  ✗ FAILED: {str(e)}\n")
            results.append(False)
    
    # Test 5: Invalid URL
    print("Test 5: Error handling (invalid URL)...")
    try:
        response = requests.post(
            f"{BASE_URL}/shorten",
            json={'longUrl': 'invalid-url'},
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 400
        data = response.json()
        assert data['success'] == False
        assert 'error' in data
        print("  ✓ PASSED\n")
        results.append(True)
    except Exception as e:
        print(f"  ✗ FAILED: {str(e)}\n")
        results.append(False)
    
    # Test 6: Rate limiting
    print("Test 6: Rate limiting...")
    try:
        # Make many requests
        response_codes = []
        for i in range(105):
            response = requests.get(
                f"{BASE_URL}/",
                headers={'X-Forwarded-For': '192.168.99.99'}
            )
            response_codes.append(response.status_code)
        
        # Should have some 200s and some 429s
        has_200 = 200 in response_codes
        has_429 = 429 in response_codes
        
        assert has_200, "No successful requests"
        assert has_429, "No rate limited requests"
        
        print(f"  ✓ PASSED - 200s: {response_codes.count(200)}, 429s: {response_codes.count(429)}\n")
        results.append(True)
    except Exception as e:
        print(f"  ✗ FAILED: {str(e)}\n")
        results.append(False)
    
    # Summary
    print("="*60)
    print("SMOKE TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED - SYSTEM READY FOR DEPLOYMENT\n")
        return True
    else:
        print(f"\n✗ {total - passed} TEST(S) FAILED\n")
        return False

if __name__ == '__main__':
    try:
        success = test_smoke_all()
        exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Cannot connect to server at http://localhost:5000")
        print("Make sure the app is running: python src/app.py\n")
        exit(1)
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {str(e)}\n")
        exit(1)

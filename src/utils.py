"""
Utility Functions for URL Shortener Service
Base62 encoding, URL validation, etc.
"""

import re
from urllib.parse import urlparse

# ===== BASE62 ENCODING =====

def base62_encode(num):
    """Convert integer to base62 string"""
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if num == 0:
        return alphabet[0]
    
    result = ""
    while num > 0:
        result = alphabet[num % 62] + result
        num //= 62
    return result

def base62_decode(s):
    """Convert base62 string to integer"""
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = 0
    for char in s:
        result = result * 62 + alphabet.index(char)
    return result

# ===== URL VALIDATION =====

def is_valid_url(url):
    """Validate if URL has correct format"""
    # Check length
    if not url or len(url) > 2000:
        return False
    
    # Check protocol
    if not url.startswith(('http://', 'https://')):
        return False
    
    # Try parsing with urlparse
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

# ===== RESPONSE FORMATTING =====

def format_response(status, data=None, error=None):
    """Format API response"""
    response = {'status': status}
    if data:
        response.update(data)
    if error:
        response['error'] = error
    return response

# ===== TESTS =====

if __name__ == '__main__':
    # Test base62 encoding
    print("Testing base62 encoding:")
    print(f"  1 -> {base62_encode(1)}")
    print(f"  100 -> {base62_encode(100)}")
    print(f"  999999 -> {base62_encode(999999)}")
    
    # Test URL validation
    print("\nTesting URL validation:")
    print(f"  https://example.com: {is_valid_url('https://example.com')}")
    print(f"  example.com: {is_valid_url('example.com')}")
    print(f"  http://google.com: {is_valid_url('http://google.com')}")

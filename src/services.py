"""
Business Logic Services for URL Shortener
URLShortenerService handles shortening logic
"""

from models import Link, get_session
from utils import base62_encode, is_valid_url
from datetime import datetime

class URLShortenerService:
    """Service for shortening URLs"""
    
    @staticmethod
    def shorten_url(long_url):
        """
        Shorten a URL and store in database
        
        Args:
            long_url (str): Original URL to shorten
            
        Returns:
            dict: {shortCode, shortUrl} on success
            dict: {error} on failure
        """
        
        # Step 1: Validate URL
        if not is_valid_url(long_url):
            return {
                'success': False,
                'error': 'Invalid URL format. Must start with http:// or https://'
            }
        
        session = get_session()
        
        try:
            # Step 2: Check if URL already exists (idempotency)
            existing_link = session.query(Link).filter_by(longUrl=long_url).first()
            if existing_link:
                return {
                    'success': True,
                    'shortCode': existing_link.shortCode,
                    'shortUrl': f'http://localhost:5000/{existing_link.shortCode}',
                    'message': 'URL already shortened (idempotent)'
                }
            
            # Step 3: Generate short code (base62 encoding of ID)
            # Get next available ID
            last_link = session.query(Link).order_by(Link.id.desc()).first()
            next_id = (last_link.id + 1) if last_link else 1
            
            short_code = base62_encode(next_id)
            
            # Ensure short code is 6 chars (pad with zeros if needed)
            while len(short_code) < 6:
                short_code = '0' + short_code
            
            # Step 4: Create and store link in database
            new_link = Link(
                shortCode=short_code,
                longUrl=long_url,
                clickCount=0,
                isActive=True
            )
            session.add(new_link)
            session.commit()
            
            return {
                'success': True,
                'shortCode': short_code,
                'shortUrl': f'http://localhost:5000/{short_code}'
            }
            
        except Exception as e:
            session.rollback()
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
        finally:
            session.close()

# ===== TESTS =====

if __name__ == '__main__':
    print("Testing URLShortenerService:")
    
    # Test 1: Valid URL
    result1 = URLShortenerService.shorten_url('https://www.example.com/very/long/url')
    print(f"\nTest 1 (Valid URL):")
    print(f"  Result: {result1}")
    
    # Test 2: Duplicate URL (idempotency)
    result2 = URLShortenerService.shorten_url('https://www.example.com/very/long/url')
    print(f"\nTest 2 (Duplicate URL - Idempotency):")
    print(f"  Result: {result2}")
    print(f"  Should have same shortCode: {result1['shortCode'] == result2['shortCode']}")
    
    # Test 3: Invalid URL (no protocol)
    result3 = URLShortenerService.shorten_url('example.com')
    print(f"\nTest 3 (Invalid URL):")
    print(f"  Result: {result3}")

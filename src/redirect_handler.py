"""
Redirect Handler (TASK-2.2)
Handles redirects and logs analytics
"""

from models import Link, Analytics, get_session
from datetime import datetime
from sqlalchemy import func

class RedirectHandler:
    """Handles URL redirects and analytics logging"""
    
    @staticmethod
    def get_redirect_url(short_code):
        """
        Get original URL and log analytics
        
        Args:
            short_code: Short code to look up
            
        Returns:
            dict: {success, longUrl, message} or {success, error}
        """
        session = get_session()
        
        try:
            # Find link by short code
            link = session.query(Link).filter_by(shortCode=short_code).first()
            
            if not link:
                return {
                    'success': False,
                    'error': f'Short code "{short_code}" not found'
                }
            
            if not link.isActive:
                return {
                    'success': False,
                    'error': 'This link has been deactivated'
                }
            
            # Increment click counter
            link.clickCount += 1
            session.commit()
            
            return {
                'success': True,
                'longUrl': link.longUrl
            }
            
        except Exception as e:
            session.rollback()
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
        finally:
            session.close()
    
    @staticmethod
    def log_analytics(short_code, ip_address, referrer, user_agent, geolocation=None):
        """
        Log click analytics for a link
        
        Args:
            short_code: Short code of link
            ip_address: Client IP
            referrer: HTTP referrer
            user_agent: Browser user agent
            geolocation: Optional geo data
        """
        session = get_session()
        
        try:
            # Find link by short code
            link = session.query(Link).filter_by(shortCode=short_code).first()
            
            if not link:
                return False
            
            # Create analytics record
            analytics = Analytics(
                linkId=link.id,
                timestamp=datetime.utcnow(),
                ipAddress=ip_address,
                referrer=referrer,
                userAgent=user_agent,
                geolocation=geolocation or 'Unknown'
            )
            
            session.add(analytics)
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            print(f"Analytics logging error: {str(e)}")
            return False
        finally:
            session.close()

"""
Analytics Service (TASK-2.3)
Aggregates click data and provides statistics
"""

from models import Link, Analytics, get_session
from sqlalchemy import func, desc
from collections import Counter

class AnalyticsService:
    """Service for analytics aggregation"""
    
    @staticmethod
    def get_stats(short_code):
        """
        Get statistics for a shortened link
        
        Args:
            short_code: Short code to get stats for
            
        Returns:
            dict: Analytics data or error
        """
        session = get_session()
        
        try:
            # Find link
            link = session.query(Link).filter_by(shortCode=short_code).first()
            
            if not link:
                return {
                    'success': False,
                    'error': f'Short code "{short_code}" not found'
                }
            
            # Get all analytics for this link
            analytics = session.query(Analytics).filter_by(linkId=link.id).all()
            
            if not analytics:
                return {
                    'success': True,
                    'shortCode': short_code,
                    'longUrl': link.longUrl,
                    'totalClicks': 0,
                    'uniqueVisitors': 0,
                    'topReferrers': [],
                    'deviceBreakdown': {},
                    'createdAt': link.createdAt.isoformat()
                }
            
            # Calculate stats
            total_clicks = len(analytics)
            unique_ips = len(set(a.ipAddress for a in analytics))
            
            # Top referrers
            referrer_counts = Counter(a.referrer for a in analytics if a.referrer)
            top_referrers = [
                {'referrer': ref, 'clicks': count}
                for ref, count in referrer_counts.most_common(5)
            ]
            
            # Device breakdown (from user agent)
            device_breakdown = {
                'mobile': len([a for a in analytics if 'mobile' in a.userAgent.lower()]),
                'desktop': len([a for a in analytics if 'windows' in a.userAgent.lower() or 'mac' in a.userAgent.lower()]),
                'other': len([a for a in analytics if 'mobile' not in a.userAgent.lower() and 'windows' not in a.userAgent.lower() and 'mac' not in a.userAgent.lower()])
            }
            
            # Geographic breakdown
            geo_breakdown = Counter(a.geolocation for a in analytics if a.geolocation)
            top_locations = [
                {'location': loc, 'clicks': count}
                for loc, count in geo_breakdown.most_common(5)
            ]
            
            return {
                'success': True,
                'shortCode': short_code,
                'longUrl': link.longUrl,
                'totalClicks': total_clicks,
                'uniqueVisitors': unique_ips,
                'topReferrers': top_referrers,
                'deviceBreakdown': device_breakdown,
                'topLocations': top_locations,
                'createdAt': link.createdAt.isoformat(),
                'lastAccessed': analytics[-1].timestamp.isoformat() if analytics else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error calculating stats: {str(e)}'
            }
        finally:
            session.close()

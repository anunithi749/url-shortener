"""
Rate Limiting Module (TASK-2.4)
Tracks requests per IP and enforces 100 req/min limit
"""

from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    """Rate limiter using in-memory tracking"""
    
    def __init__(self, max_requests=100, window_seconds=60):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Max requests allowed per window (default: 100)
            window_seconds: Time window in seconds (default: 60 = 1 minute)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)  # IP -> list of timestamps
    
    def is_allowed(self, ip_address):
        """
        Check if IP is allowed to make a request
        
        Args:
            ip_address: Client IP address
            
        Returns:
            bool: True if allowed, False if rate limited
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Clean old requests outside window
        self.requests[ip_address] = [
            ts for ts in self.requests[ip_address]
            if ts > window_start
        ]
        
        # Check if limit exceeded
        if len(self.requests[ip_address]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[ip_address].append(now)
        return True
    
    def get_remaining(self, ip_address):
        """Get remaining requests for IP"""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Clean old requests
        self.requests[ip_address] = [
            ts for ts in self.requests[ip_address]
            if ts > window_start
        ]
        
        return max(0, self.max_requests - len(self.requests[ip_address]))

# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)

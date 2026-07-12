"""
URL Shortener Service - Complete Flask Application
All endpoints: POST /shorten, GET /{shortCode}, GET /stats/{shortCode}
With rate limiting, validation, logging, and analytics
TASKS 2.1 - 2.6 COMPLETE
"""

from flask import Flask, request, jsonify, redirect as flask_redirect
from services import URLShortenerService
from redirect_handler import RedirectHandler
from analytics_service import AnalyticsService
from rate_limiter import rate_limiter
from models import init_db
import logging
import os

# Initialize Flask
app = Flask(__name__)
app.config['DEBUG'] = True

# Setup logging (TASK-2.6)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database
DATABASE = os.path.join(os.path.dirname(__file__), 'links.db')

# Initialize DB
try:
    init_db()
except:
    pass

# Helper function to get client IP
def get_client_ip():
    """Get client IP from request"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ.get('HTTP_X_FORWARDED_FOR').split(',')[0]
    return request.environ.get('REMOTE_ADDR', '127.0.0.1')

# ===== MIDDLEWARE: Rate Limiting (TASK-2.4) =====

@app.before_request
def check_rate_limit():
    """Rate limiting middleware - 100 req/min per IP"""
    ip = get_client_ip()
    
    if not rate_limiter.is_allowed(ip):
        logger.warning(f"Rate limit exceeded for IP: {ip}")
        return jsonify({
            'success': False,
            'error': 'Rate limit exceeded (100 requests per minute)'
        }), 429

# ===== API ROUTES =====

@app.route('/', methods=['GET'])
def home():
    """Welcome endpoint"""
    return jsonify({
        'service': 'URL Shortener API',
        'status': 'active',
        'endpoints': {
            'shorten': 'POST /shorten',
            'redirect': 'GET /{shortCode}',
            'stats': 'GET /stats/{shortCode}'
        }
    }), 200

@app.route('/shorten', methods=['POST'])
def shorten():
    """
    POST /shorten - Shorten a URL
    
    Request: {"longUrl": "https://example.com"}
    Response: {"success": true, "shortCode": "abc123", "shortUrl": "http://localhost:5000/abc123"}
    """
    ip = get_client_ip()
    logger.info(f"POST /shorten from {ip}")
    
    # TASK-2.5: Input Validation
    if not request.is_json:
        logger.warning(f"Invalid content type from {ip}")
        return jsonify({
            'success': False,
            'error': 'Content-Type must be application/json'
        }), 400
    
    data = request.get_json()
    long_url = data.get('longUrl')
    
    if not long_url:
        logger.warning(f"Missing longUrl from {ip}")
        return jsonify({
            'success': False,
            'error': 'Missing required field: longUrl'
        }), 400
    
    # Call service
    result = URLShortenerService.shorten_url(long_url)
    
    if result.get('success'):
        logger.info(f"URL shortened: {long_url} -> {result.get('shortCode')}")
        return jsonify(result), 200
    else:
        logger.warning(f"Shorten failed: {result.get('error')}")
        return jsonify(result), 400

@app.route('/<shortCode>', methods=['GET'])
def redirect_url(shortCode):
    """
    GET /{shortCode} - Redirect to original URL
    TASK-2.2: Redirect with analytics logging
    """
    ip = get_client_ip()
    logger.info(f"GET /{shortCode} from {ip}")
    
    # Get redirect URL
    result = RedirectHandler.get_redirect_url(shortCode)
    
    if not result.get('success'):
        logger.warning(f"Redirect failed: {result.get('error')}")
        return jsonify(result), 404
    
    # Log analytics (TASK-2.2)
    referrer = request.headers.get('Referer', 'Direct')
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    RedirectHandler.log_analytics(
        short_code=shortCode,
        ip_address=ip,
        referrer=referrer,
        user_agent=user_agent
    )
    
    logger.info(f"Redirecting {shortCode} to {result.get('longUrl')}")
    
    # Return 302 redirect
    return flask_redirect(result.get('longUrl'), code=302)

@app.route('/stats/<shortCode>', methods=['GET'])
def get_stats(shortCode):
    """
    GET /stats/{shortCode} - Get analytics
    TASK-2.3: Analytics aggregation
    """
    ip = get_client_ip()
    logger.info(f"GET /stats/{shortCode} from {ip}")
    
    # Get stats
    result = AnalyticsService.get_stats(shortCode)
    
    if not result.get('success'):
        logger.warning(f"Stats failed: {result.get('error')}")
        return jsonify(result), 404
    
    logger.info(f"Stats retrieved for {shortCode}")
    return jsonify(result), 200

# ===== ERROR HANDLERS (TASK-2.5) =====

@app.errorhandler(404)
def not_found(e):
    """404 Error handler"""
    logger.warning(f"404 error: {request.path}")
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    """500 Error handler"""
    logger.error(f"500 error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

# ===== MAIN =====

if __name__ == '__main__':
    logger.info("Starting URL Shortener Service...")
    logger.info(f"Database: {DATABASE}")
    print("\n" + "="*60)
    print("URL SHORTENER SERVICE - TASKS 2.1 to 2.6 COMPLETE")
    print("="*60)
    print("\nEndpoints:")
    print("  POST   /shorten          - Create short URL")
    print("  GET    /{shortCode}      - Redirect to original")
    print("  GET    /stats/{shortCode} - Get analytics")
    print("\nTest:")
    print('  curl -X POST http://localhost:5000/shorten \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"longUrl": "https://www.example.com"}\'')
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

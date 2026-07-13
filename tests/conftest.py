"""
Pytest Configuration File (conftest.py)
Automatically loaded by pytest
Configures Python path for test imports
Provides fixtures for tests
"""

import sys
import os

# Add src directory to Python path so tests can import from it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from app import app
from models import Link, Analytics, get_session
from rate_limiter import rate_limiter  # ✅ FIX: It's 'rate_limiter' not 'limiter'

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
    session.query(Analytics).delete()
    session.query(Link).delete()
    session.commit()
    session.close()
    
    # ✅ CRITICAL FIX: Reset the rate limiter for each test
    rate_limiter.requests.clear()  # Clear all rate limiter requests

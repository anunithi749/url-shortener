"""
Database Models for URL Shortener Service
Defines SQLAlchemy ORM models for links and analytics tables
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database path
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'links.db')

# Create base class for ORM models
Base = declarative_base()

# ===== MODEL 1: Links =====

class Link(Base):
    """Represents a shortened URL"""
    __tablename__ = 'links'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    shortCode = Column(String(10), unique=True, nullable=False, index=True)
    longUrl = Column(String(2000), nullable=False, index=True)
    createdAt = Column(DateTime, default=datetime.utcnow, index=True)
    clickCount = Column(Integer, default=0)
    isActive = Column(Boolean, default=True)
    
    # Relationship to analytics
    analytics = relationship('Analytics', back_populates='link')
    
    def __repr__(self):
        return f'<Link {self.shortCode} -> {self.longUrl}>'

# ===== MODEL 2: Analytics =====

class Analytics(Base):
    """Represents a click event on a shortened link"""
    __tablename__ = 'analytics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    linkId = Column(Integer, ForeignKey('links.id'), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    ipAddress = Column(String(45), index=True)
    referrer = Column(String(500))
    userAgent = Column(String(500))
    geolocation = Column(String(100))
    
    # Relationship to links
    link = relationship('Link', back_populates='analytics')
    
    def __repr__(self):
        return f'<Analytics linkId={self.linkId} ip={self.ipAddress}>'

# ===== DATABASE SESSION =====

def get_session():
    """Create and return a database session"""
    engine = create_engine(f'sqlite:///{DATABASE_PATH}')
    Session = sessionmaker(bind=engine)
    return Session()

def init_db():
    """Initialize database with models (if not already done)"""
    engine = create_engine(f'sqlite:///{DATABASE_PATH}')
    Base.metadata.create_all(engine)
    print(f"✓ Database models initialized at {DATABASE_PATH}")

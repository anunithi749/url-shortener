"""
Database Setup Script for URL Shortener Service
Creates SQLite database with links and analytics tables with indexes
Run: python create_db.py
"""

import sqlite3
import os

DB_PATH = 'links.db'

def create_database():
    """Create SQLite database with proper schema"""
    
    # Check if DB already exists
    if os.path.exists(DB_PATH):
        print(f"✓ Database {DB_PATH} already exists. Skipping creation.")
        return
    
    # Connect to database (creates file if doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Creating database schema...")
    
    # Create links table
    cursor.execute('''
        CREATE TABLE links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shortCode VARCHAR(10) UNIQUE NOT NULL,
            longUrl VARCHAR(2000) NOT NULL,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            clickCount INTEGER DEFAULT 0,
            isActive BOOLEAN DEFAULT 1
        )
    ''')
    print("✓ Created 'links' table")
    
    # Create indexes for links table
    cursor.execute('CREATE INDEX idx_shortCode ON links(shortCode)')
    cursor.execute('CREATE INDEX idx_longUrl ON links(longUrl)')
    cursor.execute('CREATE INDEX idx_createdAt ON links(createdAt)')
    print("✓ Created indexes on links table")
    
    # Create analytics table
    cursor.execute('''
        CREATE TABLE analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            linkId INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ipAddress VARCHAR(45),
            referrer VARCHAR(500),
            userAgent VARCHAR(500),
            geolocation VARCHAR(100),
            FOREIGN KEY (linkId) REFERENCES links(id)
        )
    ''')
    print("✓ Created 'analytics' table")
    
    # Create indexes for analytics table
    cursor.execute('CREATE INDEX idx_linkId ON analytics(linkId)')
    cursor.execute('CREATE INDEX idx_timestamp ON analytics(timestamp)')
    cursor.execute('CREATE INDEX idx_ipAddress ON analytics(ipAddress)')
    print("✓ Created indexes on analytics table")
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"\n✅ Database setup complete!")
    print(f"📁 Database file: {DB_PATH}")
    print(f"📝 Tables: links, analytics")
    print(f"🔑 Indexes: shortCode (unique), linkId, timestamp, ipAddress")

if __name__ == '__main__':
    create_database()

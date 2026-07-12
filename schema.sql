-- URL Shortener Service Database Schema
-- Run this in DB Browser if you want to create tables manually
-- Or use: python create_db.py (automatic)

-- ============================================
-- Table 1: links
-- Stores shortened URLs
-- ============================================

CREATE TABLE links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shortCode VARCHAR(10) UNIQUE NOT NULL,
    longUrl VARCHAR(2000) NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    clickCount INTEGER DEFAULT 0,
    isActive BOOLEAN DEFAULT 1
);

-- Indexes for fast lookup
CREATE INDEX idx_shortCode ON links(shortCode);
CREATE INDEX idx_longUrl ON links(longUrl);
CREATE INDEX idx_createdAt ON links(createdAt);

-- ============================================
-- Table 2: analytics
-- Tracks every click on a shortened link
-- ============================================

CREATE TABLE analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    linkId INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ipAddress VARCHAR(45),
    referrer VARCHAR(500),
    userAgent VARCHAR(500),
    geolocation VARCHAR(100),
    FOREIGN KEY (linkId) REFERENCES links(id)
);

-- Indexes for analytics
CREATE INDEX idx_linkId ON analytics(linkId);
CREATE INDEX idx_timestamp ON analytics(timestamp);
CREATE INDEX idx_ipAddress ON analytics(ipAddress);

-- ============================================
-- Sample Queries (for testing)
-- ============================================

-- Insert a shortened link
-- INSERT INTO links (shortCode, longUrl) VALUES ('abc123', 'https://example.com/very/long/url');

-- Insert analytics data
-- INSERT INTO analytics (linkId, ipAddress, referrer, userAgent) 
-- VALUES (1, '192.168.1.1', 'google.com', 'Mozilla/5.0...');

-- Get stats for a link
-- SELECT COUNT(*) as totalClicks, 
--        COUNT(DISTINCT ipAddress) as uniqueVisitors,
--        referrer 
-- FROM analytics 
-- WHERE linkId = 1 
-- GROUP BY referrer;

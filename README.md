# URL Shortener Service

A simple, production-grade URL shortening service built with Python, Flask, and SQLite.

---

## 🚀 Quick Start

### 1. Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate              # Mac/Linux
# OR
venv\Scripts\activate                 # Windows

# Install dependencies
pip install -r requirements.txt

# Create database
python create_db.py

# Run the app
python app.py
```

### 2. Test
```bash
# Shorten a URL
curl -X POST http://localhost:5000/shorten \
  -H "Content-Type: application/json" \
  -d '{"longUrl": "https://www.example.com/very/long/url"}'

# Visit the short link (redirects to original)
curl http://localhost:5000/abc123

# Get stats
curl http://localhost:5000/stats/abc123
```

---

## 📦 What's Included

| File | Purpose |
|------|---------|
| `app.py` | Main Flask application |
| `create_db.py` | Database setup script |
| `requirements.txt` | Python dependencies |
| `tests/` | Unit and integration tests |
| `docs/` | Documentation |

---

## 🔗 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/shorten` | Create short URL |
| GET | `/{shortCode}` | Redirect to original URL |
| GET | `/stats/{shortCode}` | Get analytics |

---

## 📋 Requirements

- Python 3.9+
- Flask 2.0+
- SQLite 3

All dependencies installed via `requirements.txt`

---

## 📚 Documentation

- `docs/ARCHITECTURE.md` - System design and architecture
- `docs/API.md` - API specifications (to be created)

---

## ✅ Status

- Day 1: Setup ✓
- Day 2: Core implementation (in progress)
- Day 3: Testing & Polish (pending)

---

## 🔧 Development

```bash
# Activate environment
source venv/bin/activate

# Run tests
pytest

# Run with coverage
pytest --cov

# Run app
python app.py
```

---

**Created:** July 2026  
**Assignment:** Schwab AI-Assisted Software Engineering (A1)

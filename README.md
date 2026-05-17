# Inventory Hub - Backend

Flask-based CRUD API for managing inventory items, integrated with PostgreSQL and Redis.

## Technology Stack
- **Runtime**: Python 3.11
- **Framework**: Flask
- **ORM**: SQLAlchemy
- **Caching/Hitting**: Redis
- **Database**: PostgreSQL

## Development Setup

### Installation
```bash
pip install -r requirements.txt
```

### Running Locally
```bash
python app.py
```

## API Endpoints
- `GET /items`: List all items
- `POST /items`: Create a new item
- `PUT /items/<id>`: Update an item
- `DELETE /items/<id>`: Delete an item
- `GET /hits`: Redis-backed view counter
- `GET /health`: Health status check

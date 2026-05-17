import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import redis

# --- 1. App Initialization and Configuration ---
app = Flask(__name__)
CORS(app)

# --- Database Configuration (Leveraging Environment Variables) ---
# Read DB connection details from environment variables for production/compose setup
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASS = os.getenv('DB_PASS', 'password')
DB_NAME = os.getenv('DB_NAME', 'cruddb')
DB_PORT = os.getenv('DB_PORT', '5432')

# PostgreSQL connection URI
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Redis Configuration ---
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# --- 2. Database Model Definition ---


class Item(db.Model):
    # Set the table name
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(120), nullable=True)

    def to_dict(self):
        # Helper function to serialize the model to a dictionary
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

# --- 3. CRUD Routes Implementation ---

# CREATE (POST) - Create a new item


@app.route('/items', methods=['POST'])
def create_item():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"message": "Missing 'name' field"}), 400

    new_item = Item(
        name=data['name'],
        description=data.get('description')
    )

    db.session.add(new_item)
    db.session.commit()
    return jsonify(new_item.to_dict()), 201  # 201 Created

# READ (GET) - Get all items


@app.route('/items', methods=['GET'])
def get_all_items():
    items = Item.query.all()
    # Serialize all items into a list of dictionaries
    return jsonify([item.to_dict() for item in items])

# READ (GET) - Get a single item by ID


@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = db.session.get(Item, item_id)
    if item is None:
        return jsonify({"message": "Item not found"}), 404
    return jsonify(item.to_dict())

# UPDATE (PUT) - Update an existing item


@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = db.session.get(Item, item_id)
    if item is None:
        return jsonify({"message": "Item not found"}), 404

    data = request.get_json()

    # Update fields if provided
    if 'name' in data:
        item.name = data['name']
    if 'description' in data:
        item.description = data['description']

    db.session.commit()
    return jsonify(item.to_dict())

# DELETE (DELETE) - Delete an item


@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = db.session.get(Item, item_id)
    if item is None:
        return jsonify({"message": "Item not found"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": f"Item {item_id} deleted successfully"})

# --- 4. Redis Hit Counter ---
@app.route('/hits')
def get_hits():
    hits = r.incr('hits')
    return jsonify({"hits": hits})

# --- 5. Health Check ---
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

# --- 4. Main Execution Block ---


# Initial setup to create tables if they don't exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Use 0.0.0.0 for container access
    app.run(debug=True, host='0.0.0.0', port=os.getenv('PORT', 3000))

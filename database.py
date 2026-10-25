import os
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb://localhost:27017/"
)
_client = None
_db     = None

def get_db():
    global _client, _db
    if _db is None:
        _client = MongoClient(MONGO_URI)
        _db     = _client['Amenity']
    return _db

def init_db():
    db = get_db()

    # ── Unique indexes ────────────────────────────────────────
    db.users.create_index([('username', ASCENDING)], unique=True)
    db.prediction.create_index([('food_name', ASCENDING)], unique=True)

    # ── Seed admin user ───────────────────────────────────────
    if not db.users.find_one({'username': 'admin'}):
        db.users.insert_one({
            'username': 'admin',
            'email':    'admin@amenity.com',
            'password': 'admin123',
            'role':     'admin'
        })

    # ── Seed food items ───────────────────────────────────────
    if db.food.count_documents({}) == 0:
        foods = [
            {'food_name': 'Idli',       'category': 'Breakfast', 'price': 30,  'available_status': 1},
            {'food_name': 'Dosa',       'category': 'Breakfast', 'price': 40,  'available_status': 1},
            {'food_name': 'Pongal',     'category': 'Breakfast', 'price': 35,  'available_status': 1},
            {'food_name': 'Vada',       'category': 'Breakfast', 'price': 25,  'available_status': 1},
            {'food_name': 'Meals',       'category': 'Lunch',     'price': 80,  'available_status': 1},
            {'food_name': 'Fried Rice',  'category': 'Lunch',     'price': 70,  'available_status': 1},
            {'food_name': 'Biryani',     'category': 'Lunch',     'price': 120, 'available_status': 1},
            {'food_name': 'Tomato Rice', 'category': 'Lunch',     'price': 60,  'available_status': 1},
            {'food_name': 'Samosa',     'category': 'Snacks',    'price': 15,  'available_status': 1},
            {'food_name': 'Puffs',      'category': 'Snacks',    'price': 20,  'available_status': 1},
            {'food_name': 'Tea',        'category': 'Snacks',    'price': 10,  'available_status': 1},
            {'food_name': 'Coffee',     'category': 'Snacks',    'price': 15,  'available_status': 1},
            {'food_name': 'Chapati',    'category': 'Dinner',    'price': 40,  'available_status': 1},
            {'food_name': 'Dosa',       'category': 'Dinner',    'price': 40,  'available_status': 1},
            {'food_name': 'Parotta',    'category': 'Dinner',    'price': 50,  'available_status': 1},
        ]
        db.food.insert_many(foods)

    # ── Seed prediction data ──────────────────────────────────
    if db.prediction.count_documents({}) == 0:
        preds = [
            {'food_name': 'Biryani',    'predicted_demand': 75, 'demand_level': 'High'},
            {'food_name': 'Dosa',       'predicted_demand': 60, 'demand_level': 'High'},
            {'food_name': 'Meals',      'predicted_demand': 55, 'demand_level': 'High'},
            {'food_name': 'Idli',       'predicted_demand': 45, 'demand_level': 'Medium'},
            {'food_name': 'Fried Rice', 'predicted_demand': 40, 'demand_level': 'Medium'},
            {'food_name': 'Pongal',     'predicted_demand': 30, 'demand_level': 'Medium'},
            {'food_name': 'Chapati',    'predicted_demand': 25, 'demand_level': 'Medium'},
            {'food_name': 'Parotta',    'predicted_demand': 22, 'demand_level': 'Medium'},
            {'food_name': 'Vada',       'predicted_demand': 18, 'demand_level': 'Low'},
            {'food_name': 'Samosa',     'predicted_demand': 15, 'demand_level': 'Low'},
            {'food_name': 'Coffee',     'predicted_demand': 12, 'demand_level': 'Low'},
            {'food_name': 'Tea',        'predicted_demand': 10, 'demand_level': 'Low'},
            {'food_name': 'Puffs',      'predicted_demand':  8, 'demand_level': 'Low'},
        ]
        db.prediction.insert_many(preds)

    print("[OK] MongoDB connected and seed data ready.")

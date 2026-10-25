from pymongo import MongoClient
import sys

client = MongoClient('mongodb://localhost:27017/')
db = client['Amenity']

existing = db.food.find_one({'food_name': 'Curd Rice', 'category': 'Lunch'})
if not existing:
    result = db.food.insert_one({'food_name': 'Curd Rice', 'category': 'Lunch', 'price': 50, 'available_status': 1})
    sys.stdout.write('Curd Rice added to Lunch: ' + str(result.inserted_id) + '\n')
else:
    sys.stdout.write('Already exists: ' + str(existing['_id']) + '\n')
sys.stdout.flush()
client.close()

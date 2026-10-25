import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import init_db, get_db
from datetime import datetime
from bson import ObjectId

app = Flask(__name__)
app.secret_key = os.environ.get("amenity_food_secret_2024", "temporary-local-key")

# ─── Helpers ────────────────────────────────────────────────────────────────

def get_time_slot():
    hour = datetime.now().hour
    if 6 <= hour < 11:
        return 'Breakfast'
    elif 11 <= hour < 16:
        return 'Lunch'
    elif 16 <= hour < 19:
        return 'Snacks'
    elif 19 <= hour < 22:
        return 'Dinner'
    else:
        return None

ALTERNATIVES = {
    'Idli':       ['Dosa', 'Pongal', 'Vada'],
    'Dosa':       ['Idli', 'Pongal', 'Vada'],
    'Pongal':     ['Idli', 'Dosa', 'Vada'],
    'Vada':       ['Idli', 'Dosa', 'Pongal'],
    'Meals':      ['Fried Rice', 'Biryani'],
    'Fried Rice': ['Meals', 'Biryani'],
    'Biryani':    ['Fried Rice', 'Meals'],
    'Samosa':     ['Puffs', 'Tea', 'Coffee'],
    'Puffs':      ['Samosa', 'Tea', 'Coffee'],
    'Tea':        ['Coffee'],
    'Coffee':     ['Tea'],
    'Chapati':    ['Dosa', 'Parotta'],
    'Parotta':    ['Chapati', 'Dosa'],
}

def food_id(doc):
    """Return string version of _id to use as food id in templates."""
    return str(doc['_id'])

def to_list(cursor):
    result = []
    for doc in cursor:
        doc['id'] = str(doc['_id'])
        doc.pop('_id', None)
        result.append(doc)
    return result

# ─── Auth ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db   = get_db()
        user = db.users.find_one({'username': username, 'password': password})
        if user:
            session['user_id']  = str(user['_id'])
            session['username'] = user['username']
            session['role']     = user['role']
            return redirect(url_for('admin_dashboard') if user['role'] == 'admin' else url_for('dashboard'))
        error = 'Invalid username or password.'
    return render_template('login.html', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        email    = request.form['email']
        password = request.form['password']
        confirm  = request.form['confirm']
        if password != confirm:
            error = 'Passwords do not match.'
        else:
            db = get_db()
            if db.users.find_one({'username': username}):
                error = 'Username already taken.'
            else:
                db.users.insert_one({
                    'username': username,
                    'email':    email,
                    'password': password,
                    'role':     'customer'
                })
                return redirect(url_for('login'))
    return render_template('signup.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ─── Customer ────────────────────────────────────────────────────────────────

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    slot  = get_time_slot()
    db    = get_db()
    foods = to_list(db.food.find({'category': slot}).sort('food_name', 1)) if slot else []
    return render_template('dashboard.html', foods=foods, slot=slot,
                           now=datetime.now().strftime('%I:%M %p'),
                           username=session['username'])

@app.route('/menu')
def menu():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db    = get_db()
    slot  = get_time_slot()
    foods = to_list(db.food.find().sort([('category', 1), ('food_name', 1)]))
    return render_template('menu.html', foods=foods, slot=slot,
                           username=session['username'])

@app.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('cart.html', username=session['username'])

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    data  = request.get_json()
    items = data.get('items', [])
    name  = data.get('customer_name', session['username'])
    if not items:
        return jsonify({'success': False, 'message': 'Cart is empty'})
    db        = get_db()
    order_ids = []
    for item in items:
        food = db.food.find_one({'_id': ObjectId(item['id'])})
        if not food:
            continue
        qty   = int(item['qty'])
        total = food['price'] * qty
        res   = db.orders.insert_one({
            'customer_name': name,
            'food_id':       str(food['_id']),
            'food_name':     food['food_name'],
            'quantity':      qty,
            'unit_price':    food['price'],
            'total_amount':  total,
            'order_date':    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        order_ids.append(str(res.inserted_id))

        # update prediction
        pred = db.prediction.find_one({'food_name': food['food_name']})
        if pred:
            new_demand = pred['predicted_demand'] + qty
            level = 'High' if new_demand >= 50 else 'Medium' if new_demand >= 20 else 'Low'
            db.prediction.update_one(
                {'food_name': food['food_name']},
                {'$set': {'predicted_demand': new_demand, 'demand_level': level}}
            )
        else:
            level = 'High' if qty >= 50 else 'Medium' if qty >= 20 else 'Low'
            db.prediction.insert_one({
                'food_name':        food['food_name'],
                'predicted_demand': qty,
                'demand_level':     level
            })
    return jsonify({'success': True, 'order_ids': order_ids})

@app.route('/bill_multi')




def bill_multi():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    ids_param = request.args.get('ids', '')
    if not ids_param:
        return redirect(url_for('dashboard'))
    db      = get_db()
    id_list = [ObjectId(i) for i in ids_param.split(',') if i.strip()]
    orders  = to_list(db.orders.find({'_id': {'$in': id_list}}))
    grand_total = sum(o['total_amount'] for o in orders)
    return render_template('bill.html', orders=orders, grand_total=grand_total,
                           now=datetime.now().strftime('%d-%m-%Y %I:%M %p'),
                           username=session['username'])

# ─── API ─────────────────────────────────────────────────────────────────────

@app.route('/api/food/<food_id>')
def api_food(food_id):
    db = get_db()
    try:
        food = db.food.find_one({'_id': ObjectId(food_id)})
    except Exception:
        return jsonify({'available': False})
    if not food:
        return jsonify({'available': False})
    alts = []
    if not food['available_status']:
        names = ALTERNATIVES.get(food['food_name'], [])
        for n in names:
            a = db.food.find_one({'food_name': n, 'available_status': 1})
            if a:
                alts.append({'id': str(a['_id']), 'name': a['food_name'], 'price': a['price']})
    return jsonify({
        'id':           str(food['_id']),
        'name':         food['food_name'],
        'price':        food['price'],
        'available':    bool(food['available_status']),
        'alternatives': alts
    })

# ─── Admin ───────────────────────────────────────────────────────────────────

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db   = get_db()
        user = db.users.find_one({'username': username, 'password': password, 'role': 'admin'})
        if user:
            session['user_id']  = str(user['_id'])
            session['username'] = user['username']
            session['role']     = user['role']
            return redirect(url_for('admin_dashboard'))
        error = 'Invalid admin credentials.'
    return render_template('admin_login.html', error=error)

@app.route('/admin')
@admin_required
def admin_dashboard():
    db        = get_db()
    foods     = to_list(db.food.find().sort('category', 1))
    orders    = to_list(db.orders.find().sort('order_date', -1).limit(50))
    preds     = to_list(db.prediction.find().sort('predicted_demand', -1))
    rev_pipe  = list(db.orders.aggregate([{'$group': {'_id': None, 'total': {'$sum': '$total_amount'}}}]))
    total_rev = rev_pipe[0]['total'] if rev_pipe else 0
    total_ord = db.orders.count_documents({})
    return render_template('admin.html', foods=foods, orders=orders, preds=preds,
                           total_rev=total_rev, total_ord=total_ord,
                           username=session['username'])

@app.route('/admin/add_food', methods=['POST'])
@admin_required
def add_food():
    db = get_db()
    db.food.insert_one({
        'food_name':        request.form['food_name'],
        'category':         request.form['category'],
        'price':            float(request.form['price']),
        'available_status': int(request.form['available_status']),
        'image_url':        request.form.get('image_url', '').strip()
    })
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_food/<food_id>', methods=['POST'])
@admin_required
def update_food(food_id):
    db = get_db()
    db.food.update_one(
        {'_id': ObjectId(food_id)},
        {'$set': {
            'food_name':        request.form['food_name'],
            'category':         request.form['category'],
            'price':            float(request.form['price']),
            'available_status': int(request.form['available_status']),
            'image_url':        request.form.get('image_url', '').strip()
        }}
    )
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_food/<food_id>', methods=['POST'])
@admin_required
def delete_food(food_id):
    db = get_db()
    db.food.delete_one({'_id': ObjectId(food_id)})
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, use_reloader=False)

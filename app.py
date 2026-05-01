import os

if not os.path.exists("database.db"):
    import init_db
from flask import Flask, render_template, request, jsonify, redirect, session
from twilio.rest import Client
from dotenv import load_dotenv
import os
from twilio.rest import Client

import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# 🔐 Login Credentials
USERNAME = "admin"
PASSWORD = "1234"

# 🔑 Twilio Credentials 

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(account_sid, auth_token)

# 🗄️ Database Connection
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# 🔥 AUTO CREATE DATABASE + TABLES
def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT,
        subtotal REAL,
        gst REAL,
        total REAL,
        payment_method TEXT
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        name TEXT,
        qty INTEGER,
        price REAL
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL
    )
    ''')

    # Insert default items
    cur.execute("SELECT COUNT(*) FROM menu")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO menu (name, price) VALUES ('Pizza', 200)")
        cur.execute("INSERT INTO menu (name, price) VALUES ('Burger', 100)")
        cur.execute("INSERT INTO menu (name, price) VALUES ('Coke', 50)")

    conn.commit()
    conn.close()


# 🔐 LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect('/dashboard')
        return "Invalid Credentials ❌"

    return render_template('login.html')


# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# 📊 DASHBOARD
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect('/dashboard')
    return render_template('dashboard.html')


# 🧾 BILLING PAGE
@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect('/login')

    conn = get_db()
    menu_items = conn.execute("SELECT * FROM menu").fetchall()
    conn.close()

    return render_template('index.html', menu=menu_items)


# 🍔 ADMIN MENU
@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect('/login')

    conn = get_db()
    menu_items = conn.execute("SELECT * FROM menu").fetchall()
    conn.close()

    return render_template('admin.html', menu=menu_items)


# ➕ ADD ITEM
@app.route('/add_item', methods=['POST'])
def add_item():
    if not session.get('logged_in'):
        return redirect('/login')

    name = request.form['name']
    price = request.form['price']

    conn = get_db()
    conn.execute("INSERT INTO menu (name, price) VALUES (?, ?)", (name, price))
    conn.commit()
    conn.close()

    return jsonify({"message": "Item added"})


# ❌ DELETE ITEM
@app.route('/delete_item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    if not session.get('logged_in'):
        return redirect('/login')

    conn = get_db()
    conn.execute("DELETE FROM menu WHERE id=?", (item_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Item deleted"})


# 📋 VIEW ORDERS
@app.route('/orders')
def orders():
    if not session.get('logged_in'):
        return redirect('/login')

    conn = get_db()
    orders = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    conn.close()

    return render_template('orders.html', orders=orders)


# 💾 SAVE ORDER + SMS
@app.route('/save_order', methods=['POST'])
def save_order():
    if not session.get('logged_in'):
        return redirect('/login')

    data = request.json

    phone = data.get('phone')
    subtotal = data.get('subtotal')
    gst = data.get('gst')
    total = data.get('total')
    payment = data.get('payment', 'Cash')
    items = data.get('items', [])

    # ❌ Validation
    if not phone or not items:
        return jsonify({"error": "Invalid data"}), 400

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO orders (phone, subtotal, gst, total, payment_method) VALUES (?, ?, ?, ?, ?)",
        (phone, subtotal, gst, total, payment)
    )

    order_id = cur.lastrowid

    for item in items:
        cur.execute(
            "INSERT INTO order_items (order_id, name, qty, price) VALUES (?, ?, ?, ?)",
            (order_id, item['name'], item['qty'], item['price'])
        )

    conn.commit()
    conn.close()

    # 📲 SMS (optional)
    invoice_link = f"{request.host_url}invoice/{order_id}"

    try:
        if account_sid and auth_token:
            client.messages.create(
                body=f"Your bill: ₹{total}\n{invoice_link}. Thank you for visiting!",
                from_=twilio_number,
                to=phone
            )
    except Exception as e:
        print("SMS Error:", e)

    return jsonify({
        "message": "Order saved!",
        "invoice_url": f"/invoice/{order_id}"
    })


# 🧾 INVOICE (PUBLIC ACCESS)
@app.route('/invoice/<int:order_id>')
def invoice(order_id):
    conn = get_db()

    order = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    items = conn.execute("SELECT * FROM order_items WHERE order_id=?", (order_id,)).fetchall()

    conn.close()

    return render_template('invoice.html', order=order, items=items)


# ▶️ RUN
if __name__ == '__main__':
    init_db()
    app.run(debug=True)

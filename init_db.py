import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # 💣 reset tables (IMPORTANT)
    cur.execute("DROP TABLE IF EXISTS orders")
    cur.execute("DROP TABLE IF EXISTS order_items")
    cur.execute("DROP TABLE IF EXISTS menu")

    # 🧾 orders table
    cur.execute('''
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT,
        subtotal REAL,
        gst REAL,
        total REAL,
        payment_method TEXT
    )
    ''')

    # 🧾 order items
    cur.execute('''
    CREATE TABLE order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        name TEXT,
        qty INTEGER,
        price REAL
    )
    ''')

    # 🍔 menu table
    cur.execute('''
    CREATE TABLE menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL
    )
    ''')

    # 🍕 default menu
    cur.execute("INSERT INTO menu (name, price) VALUES ('Pizza', 200)")
    cur.execute("INSERT INTO menu (name, price) VALUES ('Burger', 100)")
    cur.execute("INSERT INTO menu (name, price) VALUES ('Coke', 50)")

    conn.commit()
    conn.close()


# 👉 RUN FUNCTION
init_db()
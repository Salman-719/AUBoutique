import socket
import sqlite3
import threading
import json
import hashlib

DB_NAME = 'auboutique.db'

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Setup database and tables if they do not exist
def setup_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Create users table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    email TEXT,
                    username TEXT UNIQUE,
                    password TEXT,
                    online INTEGER DEFAULT 0
                )''')
    
    # Create products table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    owner_id INTEGER,
                    category TEXT,
                    price REAL,
                    description TEXT,
                    image TEXT,
                    buyer_id INTEGER DEFAULT NULL,
                    FOREIGN KEY (owner_id) REFERENCES users (id),
                    FOREIGN KEY (buyer_id) REFERENCES users (id)
                )''')
    
    conn.commit()
    conn.close()

# Client handler function
def handle_client(conn, addr):
    with conn:
        print(f"Connected by {addr}")
        while True:
            request = conn.recv(1024).decode('utf-8')
            if not request:
                break
            response = process_request(request)
            conn.sendall(response.encode('utf-8'))

# Process HTTP request
def process_request(request):
    # Try splitting headers and body to prevent errors
    try:
        headers, body = request.split('\r\n\r\n', 1)
    except ValueError:
        return 'HTTP/1.1 400 Bad Request\r\n\r\n{"message": "Malformed request"}'
    
    # Parse method and path from headers
    try:
        method, path, _ = headers.split(' ', 2)
    except ValueError:
        return 'HTTP/1.1 400 Bad Request\r\n\r\n{"message": "Malformed request"}'
    
    # Route to appropriate function based on the path
    if path == '/register' and method == 'POST':
        data = json.loads(body)
        return register_user(data)
    elif path == '/login' and method == 'POST':
        data = json.loads(body)
        return login_user(data)
    elif path == '/logout' and method == 'POST':
        data = json.loads(body)
        return logout_user(data['user_id'])
    elif path == '/products' and method == 'GET':
        return list_products()
    elif path == '/add_product' and method == 'POST':
        data = json.loads(body)
        return add_product(data)
    elif path == '/buy_product' and method == 'POST':
        data = json.loads(body)
        return buy_product(data)
    elif path == '/search_product' and method == 'POST':
        data = json.loads(body)
        return search_product(data['search_term'])
    elif path == '/search_user_products' and method == 'POST':
        data = json.loads(body)
        return search_user_products(data['username'])
    else:
        return 'HTTP/1.1 404 Not Found\r\n\r\n{"message": "Not found"}'

# User registration with input validation and hashed password
def register_user(data):
    if not (data['first_name'].isalpha() and data['last_name'].isalpha()):
        return '{"message": "Names must contain only letters"}'
    if not data['email'].endswith('@mail.aub.edu'):
        return '{"message": "Email must end with @mail.aub.edu"}'
    if not data['username'] or not data['password']:
        return '{"message": "Username and password cannot be empty"}'

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        hashed_password = hash_password(data['password'])
        c.execute("INSERT INTO users (first_name, last_name, email, username, password) VALUES (?, ?, ?, ?, ?)",
                  (data['first_name'], data['last_name'], data['email'], data['username'], hashed_password))
        conn.commit()
        return '{"message": "Registration successful. Please log in."}'
    except sqlite3.IntegrityError:
        return '{"message": "Username already exists"}'
    finally:
        conn.close()

# User login and logout handling
def login_user(data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    hashed_password = hash_password(data['password'])
    c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (data['username'], hashed_password))
    user = c.fetchone()
    if user:
        c.execute("UPDATE users SET online = 1 WHERE id = ?", (user[0],))
        conn.commit()
        conn.close()
        return json.dumps({"user_id": user[0], "message": "Login successful"})
    conn.close()
    return json.dumps({"message": "Invalid credentials"})

def logout_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET online = 0 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return '{"message": "Logout successful"}'

# List, add, and search products
def list_products():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()
    return json.dumps(products)

def add_product(data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO products (name, owner_id, category, price, description, image) VALUES (?, ?, ?, ?, ?, ?)",
              (data['name'], data['owner_id'], data['category'], data['price'], data['description'], data['image']))
    conn.commit()
    conn.close()
    return '{"message": "Product added successfully"}'

def search_product(search_term):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE name LIKE ?", ('%' + search_term + '%',))
    products = c.fetchall()
    conn.close()
    return json.dumps(products)

def search_user_products(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    if user:
        c.execute("SELECT * FROM products WHERE owner_id = ?", (user[0],))
        products = c.fetchall()
        conn.close()
        return json.dumps(products)
    else:
        conn.close()
        return '{"message": "User not found"}'

# Start the server
def start_server(host='localhost', port=8080):
    setup_database()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server running on {host}:{port}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()

start_server()

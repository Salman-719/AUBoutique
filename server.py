import socket
import sqlite3
import threading
import json
import hashlib

DB_NAME = 'auboutique.db'

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Setup database and tables if they do not exist
def setup_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    email TEXT,
                    username TEXT UNIQUE,
                    password TEXT,
                    online INTEGER DEFAULT 0
                )''')
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
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY,
                    sender_id INTEGER,
                    receiver_id INTEGER,
                    message TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sender_id) REFERENCES users (id),
                    FOREIGN KEY (receiver_id) REFERENCES users (id)
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
    try:
        headers, body = request.split('\r\n\r\n', 1)
        method, path, _ = headers.split(' ', 2)
    except ValueError:
        return 'HTTP/1.1 400 Bad Request\r\n\r\n{"message": "Malformed request"}'
    
    if method == 'POST':
        data = json.loads(body)
        if path == '/register':
            return register_user(data)
        elif path == '/login':
            return login_user(data)
        elif path == '/logout':
            return logout_user(data)
        elif path == '/add_product':
            return add_product(data)
        elif path == '/buy_product':
            return buy_product(data)
        elif path == '/search_product':
            return search_product(data['search_term'])
        elif path == '/search_user_products':
            return search_user_products(data['username'])
        elif path == '/send_message':
            return send_message(data)
        elif path == '/get_messages':
            return get_messages(data['user_id'])
        elif path == '/get_online_users':
            return get_online_users()
        else:
            return 'HTTP/1.1 404 Not Found\r\n\r\n{"message": "Not found"}'
    elif method == 'GET' and path == '/products':
        return list_products()
    else:
        return 'HTTP/1.1 404 Not Found\r\n\r\n{"message": "Not found"}'

# New function to get online users
def get_online_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("SELECT username FROM users WHERE online = 1")
        online_users = c.fetchall()
        if online_users:
            users_list = [user[0] for user in online_users]  # Unpack from tuple
            response_body = json.dumps({"online_users": users_list})
            response = 'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n' + response_body
            print("Successful retrieval of online users.")  # Success debug print
            return response
        else:
            print("No online users found.")
            return 'HTTP/1.1 204 No Content\r\nContent-Type: application/json\r\n\r\n{"online_users": []}'
    except sqlite3.Error as e:
        print("SQL Error retrieving online users:", str(e))  # Specific SQL error logging
        return 'HTTP/1.1 500 Internal Server Error\r\n\r\n{"message": "Internal Server Error due to SQL error: ' + str(e) + '"}'
    finally:
        conn.close()



def send_message(data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Resolve both sender and receiver IDs
    c.execute("SELECT id, online FROM users WHERE username = ?", (data['receiver_username'],))
    receiver = c.fetchone()
    c.execute("SELECT online FROM users WHERE id = ?", (data['sender_id'],))
    sender_online = c.fetchone()
    
    if receiver and sender_online and sender_online[0] == 1 and receiver[1] == 1:
        c.execute("INSERT INTO messages (sender_id, receiver_id, message) VALUES (?, ?, ?)",
                  (data['sender_id'], receiver[0], data['message']))
        conn.commit()
        return 'HTTP/1.1 200 OK\r\n\r\n{"message": "Message sent successfully."}'
    else:
        return 'HTTP/1.1 404 Not Found\r\n\r\n{"message": "Receiver not found or not online."}'

def get_messages(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Update the SQL query to join with the users table to get the sender's username
    c.execute("""
        SELECT u.username, m.message, m.timestamp 
        FROM messages m
        JOIN users u ON u.id = m.sender_id
        WHERE m.receiver_id = ?
        ORDER BY m.timestamp DESC
    """, (user_id,))
    messages = c.fetchall()
    conn.close()
    return 'HTTP/1.1 200 OK\r\n\r\n' + json.dumps({"messages": messages})


    
def buy_product(data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        # Check if product exists and is not already bought
        c.execute("SELECT * FROM products WHERE id = ? AND buyer_id IS NULL", (data['product_id'],))
        product = c.fetchone()
        if product:
            # Mark the product as bought
            c.execute("UPDATE products SET buyer_id = ? WHERE id = ?", (data['buyer_id'], data['product_id']))
            conn.commit()
            response = {"message": "Product purchase successful"}
        else:
            response = {"message": "Product not available or already sold"}
    except Exception as e:
        response = {"message": str(e)}
    finally:
        conn.close()
    return 'HTTP/1.1 200 OK\r\n\r\n' + json.dumps(response)


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

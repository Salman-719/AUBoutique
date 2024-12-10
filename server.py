import socket
import sqlite3
import threading
import json
import hashlib

DB_NAME = 'auboutique.db'

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

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
                    online INTEGER DEFAULT 0,
                    port INTEGER DEFAULT NULL,
                    ip_address TEXT DEFAULT NULL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    owner_id INTEGER,
                    category TEXT,
                    price REAL,
                    description TEXT,
                    image TEXT,
                    quantity INTEGER DEFAULT 1,
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
    c.execute('''CREATE TABLE IF NOT EXISTS product_ratings (
                    id INTEGER PRIMARY KEY,
                    product_id INTEGER,
                    user_id INTEGER,
                    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                    FOREIGN KEY (product_id) REFERENCES products (id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(product_id, user_id)
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
        return 'HTTP/1.1 400 Bad Request\r\nContent-Type: application/json\r\n\r\n{"message": "Malformed request"}'
    
    if method == 'POST':
        data = json.loads(body)
        if path == '/register':
            return register_user(data)
        elif path == '/login':
            return login_user(data)
        elif path == '/rate_product':
            return rate_product(data)
        elif path == '/get_average_rating':
            return get_average_rating(data)
        elif path == '/logout':
            return logout_user(data['user_id'])
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
        elif path == '/get_user_connection_info':
            return get_user_connection_info(data)
        else:
            return 'HTTP/1.1 404 Not Found\r\nContent-Type: application/json\r\n\r\n{"message": "Not found"}'
    elif method == 'GET' and path == '/products':
        return list_products()
    else:
        return 'HTTP/1.1 404 Not Found\r\nContent-Type: application/json\r\n\r\n{"message": "Not found"}'

def list_products():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM products")
        products = c.fetchall()
        # Structure the response data as JSON
        response = [
            {
                "id": product[0],
                "name": product[1],
                "owner_id": product[2],
                "category": product[3],
                "price": product[4],
                "description": product[5],
                "image": product[6],
                "quantity": product[7],
                "buyer_id": product[8]
            } 
            for product in products
        ]
    except Exception as e:
        response = {"message": str(e)}
    finally:
        conn.close()
    
    # Return HTTP response with JSON data
    return 'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n' + json.dumps(response)


def rate_product(data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        # Insert or update the rating
        c.execute('''
            INSERT INTO product_ratings (product_id, user_id, rating)
            VALUES (?, ?, ?)
            ON CONFLICT(product_id, user_id) DO UPDATE SET rating = excluded.rating
        ''', (data['product_id'], data['user_id'], data['rating']))
        conn.commit()
        response = {"message": "Rating submitted successfully"}
    except Exception as e:
        response = {"message": str(e)}
    finally:
        conn.close()
    return 'HTTP/1.1 200 OK\r\n\r\n' + json.dumps(response)
    
def get_average_rating(data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('''
            SELECT AVG(rating) as average_rating FROM product_ratings WHERE product_id = ?
        ''', (data['product_id'],))
        avg_rating = c.fetchone()
        response = {"average_rating": avg_rating[0] if avg_rating[0] else 0}
    except Exception as e:
        response = {"message": str(e)}
    finally:
        conn.close()
    return 'HTTP/1.1 200 OK\r\n\r\n' + json.dumps(response)


# User registration
def register_user(data):
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


# User login
def login_user(data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    hashed_password = hash_password(data['password'])
    c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (data['username'], hashed_password))
    user = c.fetchone()
    
    if user:
        # Update online status, IP, and port
        c.execute("UPDATE users SET online = 1, port = ?, ip_address = ? WHERE id = ?", 
          (data['port'], data['ip_address'], user[0]))

        conn.commit()
        conn.close()
        return json.dumps({"user_id": user[0], "message": "Login successful"})
    
    conn.close()
    return json.dumps({"message": "Invalid credentials"})

def get_user_connection_info(data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT ip_address, port FROM users WHERE username = ? AND online = 1", (data['username'],))
    user_info = c.fetchone()
    conn.close()
    
    if user_info:
        return json.dumps({"ip_address": user_info[0], "port": user_info[1]})
    else:
        return '{"message": "User is not online"}'

# User logout
def logout_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET online = 0, port = NULL WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return '{"message": "Logout successful"}'

# Add product
def add_product(data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO products (name, owner_id, category, price, description, image, quantity) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (data['name'], data['owner_id'], data['category'], data['price'], data['description'], data['image'], data['quantity']))
    conn.commit()
    conn.close()
    return '{"message": "Product added successfully"}'


# Buy product
def buy_product(data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        # Check if product exists and has available quantity
        c.execute("SELECT quantity FROM products WHERE id = ? AND buyer_id IS NULL", (data['product_id'],))
        product = c.fetchone()
        if product and product[0] > 0:
            # Decrement quantity
            new_quantity = product[0] - 1
            if new_quantity == 0:
                # Mark as sold out by assigning a buyer_id
                c.execute("UPDATE products SET buyer_id = ?, quantity = ? WHERE id = ?", (data['buyer_id'], new_quantity, data['product_id']))
            else:
                c.execute("UPDATE products SET quantity = ? WHERE id = ?", (new_quantity, data['product_id']))
            conn.commit()
            response = {"message": "Product purchase successful"}
        else:
            response = {"message": "Product not available or sold out"}
    except Exception as e:
        response = {"message": str(e)}
    finally:
        conn.close()
    return 'HTTP/1.1 200 OK\r\n\r\n' + json.dumps(response)

# Search for products by name
def search_product(search_term):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        # Search for products that match the search term
        c.execute("SELECT * FROM products WHERE name LIKE ?", ('%' + search_term + '%',))
        products = c.fetchall()
        
        # Structure the response data as JSON
        response = [
            {
                "id": product[0],
                "name": product[1],
                "owner_id": product[2],
                "category": product[3],
                "price": product[4],
                "description": product[5],
                "image": product[6],
                "quantity": product[7],
                "buyer_id": product[8]
            } 
            for product in products
        ]  
    except Exception as e:
        # Handle exceptions by returning an error message
        response = {"message": str(e)}
    finally:
        # Ensure the database connection is closed
        conn.close()
    return 'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n' + json.dumps(response)

# Search for all products by a specific user
def search_user_products(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    if user:
        try:
            c.execute("SELECT * FROM products WHERE owner_id = ?", (user[0],))
            products = c.fetchall()
            response = [
                {
                    "id": product[0],
                    "name": product[1],
                    "owner_id": product[2],
                    "category": product[3],
                    "price": product[4],
                    "description": product[5],
                    "image": product[6],
                    "quantity": product[7],
                    "buyer_id": product[8]
                } 
                for product in products
            ]  
        except Exception as e:
            # Handle exceptions by returning an error message
            response = {"message": str(e)}
        finally:
            # Ensure the database connection is closed
            conn.close()
        return 'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n' + json.dumps(response)


    else:
        conn.close()
        return '{"error": "User not found"}'

# Send a message to another user
def send_message(data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, online, port, username FROM users WHERE username = ?", (data['receiver_username'],))
    receiver = c.fetchone()
    
    if receiver and receiver[1] == 1:  # Check if receiver is online
        c.execute("INSERT INTO messages (sender_id, receiver_id, message) VALUES (?, ?, ?)",
                  (data['sender_id'], receiver[0], data['message']))
        conn.commit()
        
        receiver_port = receiver[2]
        sender_username = data.get("sender_username", "Unknown")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect(('localhost', receiver_port))
                s.sendall(json.dumps({
                    "new_message": True, 
                    "from_username": sender_username, 
                    "message": data['message']
                }).encode('utf-8'))
            except Exception as e:
                print(f"Failed to send message to {receiver_port}: {e}")
                
        return 'HTTP/1.1 200 OK\r\n\r\n{"message": "Message sent successfully."}'
    else:
        return 'HTTP/1.1 200 OK\r\n\r\n{"message": "Receiver not online."}'

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

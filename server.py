import socket
import threading
import pickle
import sqlite3

# Server setup
SERVER_HOST = 'localhost'
PORT = 8080
BUFFER_SIZE = 1024
DB_PATH = './database/auboutique.db'

# Initialize database connection
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# Initialize the database
def init_db():
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        email TEXT,
                        username TEXT UNIQUE,
                        password TEXT
                      )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        seller_id INTEGER,
                        name TEXT,
                        image BLOB,
                        price REAL,
                        description TEXT,
                        buyer_id INTEGER,
                        FOREIGN KEY(seller_id) REFERENCES users(id),
                        FOREIGN KEY(buyer_id) REFERENCES users(id)
                      )''')
    conn.commit()

# Handle client connections
def handle_client(client_socket):
    try:
        while True:
            data = client_socket.recv(BUFFER_SIZE)
            if data:
                request = pickle.loads(data)
                handle_request(client_socket, request)
            else:
                break
    except ConnectionResetError:
        pass
    finally:
        client_socket.close()

def handle_request(client_socket, request):
    action = request.get('action')
    
    if action == 'register':
        register_user(client_socket, request)
    elif action == 'login':
        login_user(client_socket, request)
    elif action == 'list_products':
        list_products(client_socket)
    # Add more actions for messaging, buying products, etc.

def register_user(client_socket, request):
    try:
        cursor.execute('INSERT INTO users (name, email, username, password) VALUES (?, ?, ?, ?)',
                       (request['name'], request['email'], request['username'], request['password']))
        conn.commit()
        client_socket.send(pickle.dumps({'status': 'ok', 'message': 'Registration successful'}))
    except sqlite3.IntegrityError:
        client_socket.send(pickle.dumps({'status': 'error', 'message': 'Username already exists'}))

def login_user(client_socket, request):
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                   (request['username'], request['password']))
    user = cursor.fetchone()
    if user:
        client_socket.send(pickle.dumps({'status': 'ok', 'message': 'Login successful'}))
    else:
        client_socket.send(pickle.dumps({'status': 'error', 'message': 'Invalid credentials'}))

def list_products(client_socket):
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    client_socket.send(pickle.dumps({'status': 'ok', 'products': products}))

# Server main loop
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_HOST, PORT))
    server.listen(5)
    print(f"Server listening on {SERVER_HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == '__main__':
    init_db()
    start_server()

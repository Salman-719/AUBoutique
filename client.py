import socket
import json
import hashlib
import threading

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def listen_for_messages(client_port):
    global messaging_active
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', client_port))
        s.listen()
        while messaging_active:
            conn, _ = s.accept()
            with conn:
                data = conn.recv(1024).decode('utf-8')
                message_data = json.loads(data)
                if message_data.get("new_message"):
                    print(f"\nMessage from {message_data['from_username']}: {message_data['message']}")

def start_listening(client_port):
    global messaging_active
    messaging_active = True
    threading.Thread(target=listen_for_messages, args=(client_port,), daemon=True).start()

def send_request(host, port, method, path, body=None):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        headers = f"{method} {path} HTTP/1.1\r\nHost: {host}\r\nContent-Type: application/json\r\n"
        if body:
            body = json.dumps(body)
            headers += f"Content-Length: {len(body)}\r\n\r\n{body}"
        else:
            headers += "\r\n"
        
        s.sendall(headers.encode('utf-8'))
        response = s.recv(4096).decode('utf-8')
        
        parts = response.split('\r\n\r\n', 1)
        json_part = parts[1] if len(parts) > 1 else parts[0]
        
        try:
            return json.loads(json_part)
        except json.JSONDecodeError:
            print("Failed to decode JSON from server response")
            print("Raw response:", response)
            return {"error": "Failed to decode JSON from server response"}

def register_user(client_port):
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    email = input("Email (must end with @mail.aub.edu): ")
    username = input("Username: ")
    password = hash_password(input("Password: "))
    data = {"first_name": first_name, "last_name": last_name, "email": email, "username": username, "password": password}
    response = send_request('localhost', 8080, 'POST', '/register', data)
    print(response.get("message", "Registration error"))

def login_user(client_port):
    username = input("Username: ")
    password = hash_password(input("Password: "))
    data = {"username": username, "password": password, "port": client_port}
    response = send_request('localhost', 8080, 'POST', '/login', data)
    if "user_id" in response:
        print(response["message"])
        return response["user_id"], username
    else:
        print(response.get("message", "Login error"))
        return None, None

def logout_user(user_id):
    response = send_request('localhost', 8080, 'POST', '/logout', {"user_id": user_id})
    print(response.get("message", "Logout error"))

def add_product(user_id):
    name = input("Product Name: ")
    category = input("Category: ")
    price = float(input("Price: "))
    description = input("Description: ")
    image = input("Image URL: ")
    data = {
        "name": name,
        "owner_id": user_id,
        "category": category,
        "price": price,
        "description": description,
        "image": image
    }
    response = send_request('localhost', 8080, 'POST', '/add_product', data)
    print(response.get("message", "Error adding product"))

def list_products():
    response = send_request('localhost', 8080, 'GET', '/products')
    if "error" not in response:
        print("Products List:", response)
    else:
        print(response["error"])

def buy_product(user_id):
    product_id = int(input("Enter Product ID to buy: "))
    data = {"buyer_id": user_id, "product_id": product_id}
    response = send_request('localhost', 8080, 'POST', '/buy_product', data)
    print(response.get("message", "Error buying product"))

def search_product():
    search_term = input("Enter product name to search: ")
    data = {"search_term": search_term}
    response = send_request('localhost', 8080, 'POST', '/search_product', data)
    if "error" not in response:
        print("Search Results:", response)
    else:
        print(response["error"])

def search_user_products():
    username = input("Enter username to view their products: ")
    data = {"username": username}
    response = send_request('localhost', 8080, 'POST', '/search_user_products', data)
    if "error" not in response:
        print("User's Products:", response)
    else:
        print(response["error"])

def messaging_page(user_id, username, client_port):
    global messaging_active
    messaging_active = True
    start_listening(client_port)
    try:
        while messaging_active:
            action = input("1. Send Message\n2. Exit Messaging\n> ")
            if action == '1':
                receiver_username = input("Enter receiver's username: ")
                message = input("Enter your message: ")
                data = {"sender_id": user_id, "sender_username": username, "receiver_username": receiver_username, "message": message}
                response = send_request('localhost', 8080, 'POST', '/send_message', data)
                print(response.get("message", "Error sending message"))
            elif action == '2':
                messaging_active = False
            else:
                print("Invalid choice.")
    finally:
        messaging_active = False

def logged_in_menu(user_id, username, client_port):
    while True:
        choice = input("1. Messaging Page\n2. List Products\n3. Add Product\n4. Buy Product\n5. Search Products\n6. Search User Products\n7. Logout\n> ")
        if choice == '1':
            messaging_page(user_id, username, client_port)
        elif choice == '2':
            list_products()
        elif choice == '3':
            add_product(user_id)
        elif choice == '4':
            buy_product(user_id)
        elif choice == '5':
            search_product()
        elif choice == '6':
            search_user_products()
        elif choice == '7':
            logout_user(user_id)
            break
        else:
            print("Invalid choice.")

def main():
    print("Welcome to AUBoutique")
    client_port = int(input("Enter a unique port number to use: "))
    while True:
        choice = input("1. Register\n2. Login\n3. Quit\n> ")
        if choice == '1':
            register_user(client_port)
        elif choice == '2':
            user_id, username = login_user(client_port)
            if user_id:
                logged_in_menu(user_id, username, client_port)
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

main()

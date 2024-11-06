import socket
import json
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

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
            return {"error": "Failed to decode JSON from server response"}

def view_online_users():
    response = send_request('localhost', 8080, 'POST', '/get_online_users')
    if "online_users" in response:
        online_users = response["online_users"]
        if online_users:
            print("Online users:")
            for user in online_users:
                print(user)
        else:
            print("No users are currently online.")
    else:
        print("Failed to retrieve online users.")

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
    if "error" not in response:
        print("Purchase Response:", response)
    else:
        print(response["error"])

def register_user():
    while True:
        first_name = input("First Name: ")
        last_name = input("Last Name: ")
        if not first_name.isalpha() or not last_name.isalpha():
            print("Invalid input. First and last name must contain only letters.")
            continue
        email = input("AUB Email: ")
        if not email.endswith('@mail.aub.edu'):
            print("Invalid email format.")
            continue
        username = input("Username: ")
        password = hash_password(input("Password: "))
        data = {"first_name": first_name, "last_name": last_name, "email": email, "username": username, "password": password}
        response = send_request('localhost', 8080, 'POST', '/register', data)
        if "error" not in response:
            print(response["message"])
            break
        else:
            print(response["error"])

def login_user():
    username = input("Username: ")
    password = hash_password(input("Password: "))
    data = {"username": username, "password": password}
    response = send_request('localhost', 8080, 'POST', '/login', data)
    if "error" not in response:
        return response
    else:
        print(response["error"])
        return None

def logout_user(user_id):
    response = send_request('localhost', 8080, 'POST', '/logout', {"user_id": user_id})
    if "error" not in response:
        print(response["message"])
    else:
        print(response["error"])

def add_product(user_id):
    data = {
        "name": input("Product Name: "),
        "owner_id": user_id,
        "category": input("Category: "),
        "price": float(input("Price: ")),
        "description": input("Description: "),
        "image": input("Image URL: ")
    }
    response = send_request('localhost', 8080, 'POST', '/add_product', data)
    if "error" not in response:
        print(response["message"])
    else:
        print(response["error"])

def search_product():
    search_term = input("Enter product name to search: ")
    data = {"search_term": search_term}
    response = send_request('localhost', 8080, 'POST', '/search_product', data)
    if "error" not in response:
        print(response)
    else:
        print(response["error"])

def search_user_products():
    username = input("Enter username to view their products: ")
    data = {"username": username}
    response = send_request('localhost', 8080, 'POST', '/search_user_products', data)
    if "error" not in response:
        print(response)
    else:
        print(response["error"])

# Send direct message without storage
def send_direct_message(user_id):
    response = send_request('localhost', 8080, 'POST', '/get_online_users')
    online_users = response.get("online_users", [])
    if online_users:
        print("Online users:")
        for user in online_users:
            print(user)
        receiver_username = input("Enter the username of the user you want to message: ")
        
        if receiver_username in online_users:
            message = input("Enter your message: ")
            data = {
                "sender_id": user_id,
                "receiver_username": receiver_username,
                "message": message
            }
            response = send_request('localhost', 8080, 'POST', '/send_message_direct', data)
            print(response.get("message", "Message sending failed."))
        else:
            print("Invalid username selected.")
    else:
        print("No users are currently online.")

def view_messages(user_id):
    response = send_request('localhost', 8080, 'POST', '/get_messages', {"user_id": user_id})
    if "messages" in response:
        for msg in response['messages']:
            print(f"From {msg[0]}: {msg[1]} at {msg[2]}")
    else:
        print("No messages or failed to retrieve messages.")

# Logged-in user menu
def logged_in_menu(user_id):
    while True:
        choice = input("1. View Products\n2. Add Product\n3. Buy Product\n4. Search Products\n5. Search User Products\n6. Send Direct Message\n7. View Messages\n8. Logout\n> ")
        if choice == '1':
            list_products()
        elif choice == '2':
            add_product(user_id)
        elif choice == '3':
            buy_product(user_id)
        elif choice == '4':
            search_product()
        elif choice == '5':
            search_user_products()
        elif choice == '6':
            send_direct_message(user_id)
        elif choice == '7':
            view_messages(user_id)
        elif choice == '8':
            logout_user(user_id)
            print("Logged out successfully. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

# Main menu
def main():
    print("Welcome to AUBoutique")
    while True:
        choice = input("1. Register\n2. Login\n3. Quit\n> ")
        
        if choice == '1':
            register_user()
        elif choice == '2':
            response = login_user()
            if response and "user_id" in response:
                print(response["message"])
                logged_in_menu(response["user_id"])
            elif response:
                print(response["message"])
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

main()

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
        return json.loads(response.split('\r\n\r\n')[1])

def register_user():
    while True:
        first_name = input("First Name (letters only): ")
        last_name = input("Last Name (letters only): ")
        if not first_name.isalpha() or not last_name.isalpha():
            print("Invalid input. First and last name must contain only letters.")
            continue
        email = input("Email (must end with @mail.aub.edu): ")
        if not email.endswith('@mail.aub.edu'):
            print("Invalid email format.")
            continue
        username = input("Username: ")
        password = hash_password(input("Password: "))
        data = {"first_name": first_name, "last_name": last_name, "email": email, "username": username, "password": password}
        response = send_request('localhost', 8080, 'POST', '/register', data)
        print(response["message"])
        break

def login_user():
    username = input("Username: ")
    password = hash_password(input("Password: "))
    data = {"username": username, "password": password}
    response = send_request('localhost', 8080, 'POST', '/login', data)
    return response

def logout_user(user_id):
    response = send_request('localhost', 8080, 'POST', '/logout', {"user_id": user_id})
    print(response["message"])

def list_products():
    response = send_request('localhost', 8080, 'GET', '/products')
    print(response)

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
    print(response["message"])

def search_product():
    search_term = input("Enter product name to search: ")
    data = {"search_term": search_term}
    response = send_request('localhost', 8080, 'POST', '/search_product', data)
    print(response)

def search_user_products():
    username = input("Enter username to view their products: ")
    data = {"username": username}
    response = send_request('localhost', 8080, 'POST', '/search_user_products', data)
    print(response)

def logged_in_menu(user_id):
    while True:
        choice = input("1. View Products\n2. Add Product\n3. Buy Product\n4. Search Products\n5. Search User Products\n6. Logout\n> ")
        
        if choice == '1':
            list_products()
        elif choice == '2':
            add_product(user_id)
        elif choice == '3':
            product_id = int(input("Enter Product ID to buy: "))
            data = {"buyer_id": user_id, "product_id": product_id}
            print(send_request('localhost', 8080, 'POST', '/buy_product', data)["message"])
        elif choice == '4':
            search_product()
        elif choice == '5':
            search_user_products()
        elif choice == '6':
            logout_user(user_id)
            break
        else:
            print("Invalid choice. Please try again.")

def main():
    print("Welcome to AUBoutique")
    while True:
        choice = input("1. Register\n2. Login\n3. Quit\n> ")
        
        if choice == '1':
            register_user()
        elif choice == '2':
            response = login_user()
            if "user_id" in response:
                print(response["message"])
                logged_in_menu(response["user_id"])
            else:
                print(response["message"])
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

main()

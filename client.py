import socket
import pickle

SERVER_HOST = 'localhost'
PORT = 8080
BUFFER_SIZE = 1024

# Client-side functions
def register():
    name = input("Enter your name: ")
    email = input("Enter your email: ")
    username = input("Enter a username: ")
    password = input("Enter a password: ")
    
    request = {
        'action': 'register',
        'name': name,
        'email': email,
        'username': username,
        'password': password
    }
    
    send_request(request)

def login():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    
    request = {
        'action': 'login',
        'username': username,
        'password': password
    }
    
    send_request(request)

def list_products():
    request = {'action': 'list_products'}
    send_request(request)

def send_request(request):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_HOST, PORT))
    client.send(pickle.dumps(request))
    
    response = pickle.loads(client.recv(BUFFER_SIZE))
    print(response.get('message'))
    if response.get('products'):
        for product in response['products']:
            print(product)
    
    client.close()

def main_menu():
    while True:
        print("\n1. Register\n2. Login\n3. View Products\n4. Exit")
        choice = input("Select an option: ")
        
        if choice == '1':
            register()
        elif choice == '2':
            login()
        elif choice == '3':
            list_products()
        elif choice == '4':
            break
        else:
            print("Invalid option, try again.")

if __name__ == '__main__':
    main_menu()

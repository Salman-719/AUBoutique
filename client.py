import socket
import json
import hashlib
import threading
import requests

class AUBoutique:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.user_id = None
        self.username = None
        self.client_port = None
        self.messaging_active = False
        self.listener_thread = None

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def listen_for_messages(self, chat_page):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', self.client_port))
            s.listen()
            while self.messaging_active:
                conn, _ = s.accept()
                with conn:
                    try:
                        data = conn.recv(1024).decode('utf-8')
                        message_data = json.loads(data)
                        # Call the ChatPage method to update the UI
                        chat_page.display_received_message(
                            message_data['from_username'],
                            message_data['message']
                        )
                    except Exception as e:
                        print(f"Error receiving message: {e}")


    def start_listening(self, chat_page):
        self.messaging_active = True
        self.listener_thread = threading.Thread(target=self.listen_for_messages, args=(chat_page,), daemon=True)
        self.listener_thread.start()


    def stop_listening(self):
        self.messaging_active = False
        if self.listener_thread:
            self.listener_thread.join()

    def send_request(self, method, path, body=None):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            headers = f"{method} {path} HTTP/1.1\r\nHost: {self.host}\r\nContent-Type: application/json\r\n"
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

    def register_user(self, first_name, last_name, email, username, password):
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "username": username,
            "password": self.hash_password(password)
        }
        response = self.send_request('POST', '/register', data)
        return response

    def login_user(self, username, password, client_port):
        try:
            self.client_port = client_port
            ip_address = socket.gethostbyname(socket.gethostname())
            data = {
                "username": username,
                "password": self.hash_password(password),
                "port": client_port,
                "ip_address": ip_address
            }
            response = self.send_request('POST', '/login', data)

            if "user_id" in response:
                self.user_id = response["user_id"]
                self.username = username
                return response
            else:
                # Handle case where login fails but no explicit error is raised
                return {"error": "Login failed. Please check your credentials."}
        except Exception as e:
            # Log or handle the exception
            return {"error": "An error occurred during login.", "details": str(e)}

    def logout_user(self):
        response = self.send_request('POST', '/logout', {"user_id": self.user_id})
        self.user_id = None
        self.username = None
        return response

    def add_product(self, name, category, price, description, image, quantity):
        data = {
            "name": name,
            "owner_id": self.user_id,
            "category": category,
            "price": price,
            "description": description,
            "image": image,
            "quantity": quantity
        }
        response = self.send_request('POST', '/add_product', data)
        return response

    def list_products(self):
        response = self.send_request('GET', '/products')
        return response

    def buy_product(self, product_id):
        data = {"buyer_id": self.user_id, "product_id": product_id}
        response = self.send_request('POST', '/buy_product', data)
        return response

    def search_product(self, search_term):
        data = {"search_term": search_term}
        response = self.send_request('POST', '/search_product', data)
        return response

    def search_user_products(self, username):
        data = {"username": username}
        response = self.send_request('POST', '/search_user_products', data)
        return response

    def rate_product(self, product_id, rating):
        data = {"user_id": self.user_id, "product_id": product_id, "rating": rating}
        response = self.send_request('POST', '/rate_product', data)
        return response

    def view_average_rating(self, product_id):
        data = {"product_id": product_id}
        response = self.send_request('POST', '/get_average_rating', data)
        return response

    def get_connection_info(self, username):
        data = {"username": username}
        response = self.send_request('POST', '/get_user_connection_info', data)
        if "ip_address" in response and "port" in response:
            return response["ip_address"], response["port"]
        return None, None

    def p2p_chat(self, receiver_username, message):
        ip, port = self.get_connection_info(receiver_username)
        if ip and port:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((ip, port))
                    s.sendall(json.dumps({
                        "from_username": self.username,
                        "message": message
                    }).encode('utf-8'))
                    return {"message": "Message sent successfully"}
                except Exception as e:
                    return {"error": f"Failed to send message: {e}"}
        return {"error": "Could not retrieve user connection info"}

    def get_currency_rates(self, base_currency):
        try:
            url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get('rates', {})
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

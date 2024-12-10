import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, 
    QLabel, QLineEdit, QPushButton, QMessageBox, QFormLayout, QHBoxLayout, QListWidget
)
from PyQt5.QtCore import Qt
from client import AUBoutique
import random

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AUBoutique")
        self.setGeometry(100, 100, 800, 600)

        # Instance of AUBoutique
        self.boutique = AUBoutique()

        # Stack of pages
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Pages
        self.pages = {}
        self.init_pages()

    def init_pages(self):
        # Login Page
        self.pages['login'] = LoginPage(self)
        self.stack.addWidget(self.pages['login'])

        # Registration Page
        self.pages['register'] = RegisterPage(self)
        self.stack.addWidget(self.pages['register'])

        # Home Page
        self.pages['home'] = HomePage(self)
        self.stack.addWidget(self.pages['home'])

        # Product Page
        self.pages['products'] = ProductsPage(self)
        self.stack.addWidget(self.pages['products'])

        # Chat Page
        self.pages['chat'] = ChatPage(self)
        self.stack.addWidget(self.pages['chat'])

        # Search Page
        self.pages['search'] = SearchPage(self)
        self.stack.addWidget(self.pages['search'])

        # Rate Product Page
        self.pages['rate'] = RateProductPage(self)
        self.stack.addWidget(self.pages['rate'])

        # Add Product Page
        self.pages['add_product'] = AddProductPage(self)
        self.stack.addWidget(self.pages['add_product'])

        # User Products Page
        self.pages['user_products'] = UserProductsPage(self)
        self.stack.addWidget(self.pages['user_products'])
        
        # Switch to Login Page initially
        self.switch_page('login')

    def switch_page(self, page_name):
        self.stack.setCurrentWidget(self.pages[page_name])


class LoginPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()

        self.info_label = QLabel("Login to AUBoutique")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        self.form_layout = QFormLayout()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.form_layout.addRow("Username:", self.username_input)
        self.form_layout.addRow("Password:", self.password_input)
        layout.addLayout(self.form_layout)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)
        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(lambda: self.parent.switch_page('register'))

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def generate_random_port(self):
        return random.randint(1024, 65535)  # Generate a port number between 1024 and 65535

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        client_port = self.generate_random_port()  # Use the generated port number

        response = self.parent.boutique.login_user(username, password, client_port)
        if "error" in response:
            QMessageBox.critical(self, "Error", response["error"])
        else:
            self.parent.boutique.start_listening()
            QMessageBox.information(self, "Success", "Logged in successfully!")
            self.parent.switch_page('home')



class RegisterPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()

        self.info_label = QLabel("Register to AUBoutique")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        self.form_layout = QFormLayout()
        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.form_layout.addRow("First Name:", self.first_name_input)
        self.form_layout.addRow("Last Name:", self.last_name_input)
        self.form_layout.addRow("Email:", self.email_input)
        self.form_layout.addRow("Username:", self.username_input)
        self.form_layout.addRow("Password:", self.password_input)
        layout.addLayout(self.form_layout)

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.handle_register)
        self.back_button = QPushButton("Back to Login")
        self.back_button.clicked.connect(lambda: self.parent.switch_page('login'))

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.back_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def handle_register(self):
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text()
        email = self.email_input.text()
        username = self.username_input.text()
        password = self.password_input.text()

        response = self.parent.boutique.register_user(first_name, last_name, email, username, password)
        if "error" in response:
            QMessageBox.critical(self, "Error", response["error"])
        else:
            QMessageBox.information(self, "Success", "Registered successfully! Please login.")
            self.parent.switch_page('login')


class HomePage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()

        self.welcome_label = QLabel("Welcome to AUBoutique!")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.welcome_label)

        self.list_products_button = QPushButton("List Products")
        self.list_products_button.clicked.connect(lambda: self.parent.switch_page('products'))
        layout.addWidget(self.list_products_button)

        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.handle_logout)
        layout.addWidget(self.logout_button)

        self.setLayout(layout)

    def handle_logout(self):
        self.parent.boutique.stop_listening()
        response = self.parent.boutique.logout_user()
        if "error" in response:
            QMessageBox.critical(self, "Error", response["error"])
        else:
            QMessageBox.information(self, "Success", "Logged out successfully!")
            self.parent.switch_page('login')


class ProductsPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()

        self.title_label = QLabel("Products")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.products_list = QListWidget()
        layout.addWidget(self.products_list)

        self.refresh_button = QPushButton("Refresh Products")
        self.refresh_button.clicked.connect(self.load_products)
        layout.addWidget(self.refresh_button)

        self.back_button = QPushButton("Back to Home")
        self.back_button.clicked.connect(lambda: self.parent.switch_page('home'))
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def load_products(self):
        response = self.parent.boutique.list_products()
        if "error" in response:
            QMessageBox.critical(self, "Error", response["error"])
        else:
            self.products_list.clear()
            for product in response.get("products", []):
                self.products_list.addItem(f"{product['name']} - {product['price']} USD")

class ProductsPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()

        self.title_label = QLabel("Products")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.products_list = QListWidget()
        layout.addWidget(self.products_list)

        self.buy_button = QPushButton("Buy Selected Product")
        self.buy_button.clicked.connect(self.handle_buy_product)
        layout.addWidget(self.buy_button)

        self.refresh_button = QPushButton("Refresh Products")
        self.refresh_button.clicked.connect(self.load_products)
        layout.addWidget(self.refresh_button)

        self.back_button = QPushButton("Back to Home")
        self.back_button.clicked.connect(lambda: self.parent.switch_page('home'))
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def load_products(self):
        response = self.parent.boutique.list_products()
        if "error" in response:
            QMessageBox.critical(self, "Error", response["error"])
        else:
            self.products_list.clear()
            for product in response.get("products", []):
                self.products_list.addItem(f"{product['id']} - {product['name']} - {product['price']} USD")

    def handle_buy_product(self):
        selected_item = self.products_list.currentItem()
        if selected_item:
            product_id = selected_item.text().split(" - ")[0]  # Extract product ID
            response = self.parent.boutique.buy_product(product_id)
            if "error" in response:
                QMessageBox.critical(self, "Error", response["error"])
            else:
                QMessageBox.information(self, "Success", "Product purchased successfully!")
                self.load_products()
        else:
            QMessageBox.warning(self, "Warning", "Please select a product to buy.")

class UserProductsPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()

        self.info_label = QLabel("Search User's Products")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.handle_search)
        layout.addWidget(self.search_button)

        self.results_list = QListWidget()
        layout.addWidget(self.results_list)

        self.back_button = QPushButton("Back to Home")
        self.back_button.clicked.connect(lambda: self.parent.switch_page('home'))
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def handle_search(self):
        username = self.username_input.text()
        response = self.parent.boutique.search_user_products(username)
        if "error" in response:
            QMessageBox.critical(self, "Error", response["error"])
        else:
            self.results_list.clear()
            for product in response.get("products", []):
                self.results_list.addItem(f"{product['name']} - {product['price']} USD")

class AddProductPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()

        self.info_label = QLabel("Add a Product")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        self.form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.category_input = QLineEdit()
        self.price_input = QLineEdit()
        self.description_input = QLineEdit()
        self.image_input = QLineEdit()
        self.quantity_input = QLineEdit()
        self.form_layout.addRow("Name:", self.name_input)
        self.form_layout.addRow("Category:", self.category_input)
        self.form_layout.addRow("Price:", self.price_input)
        self.form_layout.addRow("Description:", self.description_input)
        self.form_layout.addRow("Image URL:", self.image_input)
        self.form_layout.addRow("Quantity:", self.quantity_input)
        layout.addLayout(self.form_layout)

        self.add_button = QPushButton("Add Product")
        self.add_button.clicked.connect(self.handle_add_product)
        self.back_button = QPushButton("Back to Home")
        self.back_button.clicked.connect(lambda: self.parent.switch_page('home'))

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.back_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def handle_add_product(self):
        name = self.name_input.text()
        category = self.category_input.text()
        price = float(self.price_input.text())
        description = self.description_input.text()
        image = self.image_input.text()
        quantity = int(self.quantity_input.text())

        response = self.parent.boutique.add_product(name, category, price, description, image, quantity)
        if "error" in response:
            QMessageBox.critical(self, "Error", response["error"])
        else:
            QMessageBox.information(self, "Success", "Product added successfully!")
            self.parent.switch_page('home')

class ChatPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()

        self.info_label = QLabel("P2P Chat")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        self.form_layout = QFormLayout()
        self.receiver_input = QLineEdit()
        self.message_input = QLineEdit()
        self.form_layout.addRow("To (Username):", self.receiver_input)
        self.form_layout.addRow("Message:", self.message_input)
        layout.addLayout(self.form_layout)

        self.send_button = QPushButton("Send Message")
        self.send_button.clicked.connect(self.handle_send_message)
        self.back_button = QPushButton("Back to Home")
        self.back_button.clicked.connect(lambda: self.parent.switch_page('home'))

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.back_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def handle_send_message(self):
        receiver = self.receiver_input.text()
        message = self.message_input.text()
        response = self.parent.boutique.p2p_chat(receiver, message)
        if "error" in response:
            QMessageBox.critical(self, "Error", response["error"])
        else:
            QMessageBox.information(self, "Success", "Message sent successfully!")



class RateProductPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()

        self.info_label = QLabel("Rate a Product")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        self.form_layout = QFormLayout()
        self.product_id_input = QLineEdit()
        self.rating_input = QLineEdit()
        self.form_layout.addRow("Product ID:", self.product_id_input)
        self.form_layout.addRow("Rating (1-5):", self.rating_input)
        layout.addLayout(self.form_layout)

        self.rate_button = QPushButton("Submit Rating")
        self.rate_button.clicked.connect(self.handle_rate_product)
        self.back_button = QPushButton("Back to Products")
        self.back_button.clicked.connect(lambda: self.parent.switch_page('products'))

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.rate_button)
        button_layout.addWidget(self.back_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def handle_rate_product(self):
        product_id = self.product_id_input.text()
        rating = int(self.rating_input.text())
        response = self.parent.boutique.rate_product(product_id, rating)
        if "error" in response:
            QMessageBox.critical(self, "Error", response["error"])
        else:
            QMessageBox.information(self, "Success", "Rating submitted successfully!")


class ProductsPage(QWidget):
    # Add this function to handle view average rating
    def handle_view_average_rating(self):
        product_id = self.get_selected_product_id()
        if product_id:
            response = self.parent.boutique.view_average_rating(product_id)
            if "error" in response:
                QMessageBox.critical(self, "Error", response["error"])
            else:
                average_rating = response.get("average_rating", "N/A")
                QMessageBox.information(self, "Average Rating", f"Average Rating: {average_rating}")

class HomePage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()

        self.welcome_label = QLabel("Welcome to AUBoutique!")
        layout.addWidget(self.welcome_label)

        # Chat Button
        self.chat_button = QPushButton("Chat")
        self.chat_button.clicked.connect(lambda: parent.switch_page('chat'))
        layout.addWidget(self.chat_button)

        # Search Products Button
        self.search_button = QPushButton("Search Products")
        self.search_button.clicked.connect(lambda: parent.switch_page('search'))
        layout.addWidget(self.search_button)

        # Rate Products Button
        self.rate_button = QPushButton("Rate Products")
        self.rate_button.clicked.connect(lambda: parent.switch_page('rate'))
        layout.addWidget(self.rate_button)

        # View Products Button
        self.view_products_button = QPushButton("View Products")
        self.view_products_button.clicked.connect(lambda: parent.switch_page('products'))
        layout.addWidget(self.view_products_button)
        
        #add product
        self.add_product_button = QPushButton("Add Product")
        self.add_product_button.clicked.connect(lambda: parent.switch_page('add_product'))
        layout.addWidget(self.add_product_button)

        # Logout Button
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.handle_logout)
        layout.addWidget(self.logout_button)

        self.setLayout(layout)

    def handle_logout(self):
        # Stop listening for messages
        self.parent.boutique.stop_listening()

        # Call logout_user from AUBoutique
        response = self.parent.boutique.logout_user()
        if "error" in response:
            QMessageBox.critical(self, "Error", response["error"])
        else:
            QMessageBox.information(self, "Success", "Logged out successfully!")
            self.parent.switch_page('login')



class SearchPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()

        self.info_label = QLabel("Search Products")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        self.search_input = QLineEdit()
        layout.addWidget(self.search_input)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.handle_search)
        layout.addWidget(self.search_button)

        self.results_list = QListWidget()
        layout.addWidget(self.results_list)

        self.back_button = QPushButton("Back to Home")
        self.back_button.clicked.connect(lambda: self.parent.switch_page('home'))
        layout.addWidget(self.back_button)

        self.user_products_button = QPushButton("View User's Products")
        self.user_products_button.clicked.connect(lambda: parent.switch_page('user_products'))
        layout.addWidget(self.user_products_button)
        
        self.setLayout(layout)

    def handle_search(self):
        search_term = self.search_input.text()
        response = self.parent.boutique.search_product(search_term)
        if "error" in response:
            QMessageBox.critical(self, "Error", response["error"])
        else:
            self.results_list.clear()
            for product in response.get("products", []):
                self.results_list.addItem(f"{product['name']} - {product['price']} USD")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

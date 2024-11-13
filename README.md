# AUBoutique - An Online Marketplace for AUB Community 

AUBoutique is a user-friendly platform that facilitates the buying and selling of a variety of products such as craftwork, textbooks, and collectibles for the AUB community. This project is developed using a client-server architecture in Python.

## Features

### Client-Side
- **User Registration**: Users can sign up by providing their name, email, username, and password.
- **User Login**: Registered users can log in to their account using their credentials.
- **Product Listing**: Users can view a list of available products for sale, along with the seller's information.
- **Product Details**: Users can view products from a specific seller.
- **Live Chatting**: Users can initiate a text chat with other users through the platform if both are online.
- **Buy Products**: Buyers can select products and confirm purchases, receiving a confirmation message to collect the item from the AUB Post Office.
- **Sell Products**: Sellers can add products to the marketplace by providing a product name, image, price, and description.

### Server-Side
- **Account Management**: The server allows user registration, login, and authentication.
- **Product Management**: The server maintains a list of available products and handles product listings and purchases.
- **Text Messaging**: The server manages communication between buyers and sellers, provided both are online.
- **Database**: A simple database (e.g., SQLite) stores user accounts and product information.
- **Concurrency**: The server can handle multiple users simultaneously using multi-threading.

## Installation

### Prerequisites
- Python 3.x
- SQLite 
- Basic understanding of client-server architecture

### Clone the Repository
```bash
git clone https://github.com/Salman-719/AUBoutique.git
cd AUBoutique

```

### Install Required Libraries
To install the necessary Python libraries, run:

```bash
pip install -r requirements.txt
```
### Run the Server
Start the server by specifying a port number:

```bash
python server.py <port_number>
```
Example:
```bash
python server.py 8080
```

Run the Client
Start the client by specifying the server domain (or IP address) and port number:

```bash
python client.py <server_domain> <port_number>
```
Example:

```bash
python client.py localhost 8080
```


## Project Structure
```bash
AUBoutique/
├── client.py                # Client-side code for connecting to the server
├── server.py                # Server-side code to handle requests and manage the database
├── auboutique.db            # SQLite database file (auto-generated on first run)
├── requirements.txt         # Python dependencies (if needed)
└── README.md                # Documentation for the project

```

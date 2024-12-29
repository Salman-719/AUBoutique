# AUBoutique - An Online Marketplace for AUB Community 

AUBoutique is a user-friendly platform that facilitates the buying and selling of a variety of products such as craftwork, textbooks, and collectibles for the AUB community. This project is developed using a client-server architecture in Python.
# AUBoutique

## Overview
**AUBoutique** is an online platform designed to manage user registration, product listings, purchasing, messaging, and peer-to-peer communication, with additional features like product ratings and currency exchange rates. This project implements a hybrid client-server and peer-to-peer architecture, allowing users to interact efficiently with the system.

## System Architecture
The system utilizes both client-server and peer-to-peer (P2P) models:

- **Client-Server Communication**: Handles user registration, product management, login, and messaging.
- **Peer-to-Peer (P2P) Messaging**: After logging in, users can communicate directly with each other without routing through the server, improving efficiency and reducing server load.

## Key Features

- **User Management**:
  - Registration and login
  - User session management (online/offline status)
  
- **Product Management**:
  - Add, list, search, and buy products
  - Rate products based on user satisfaction
  
- **Messaging System**:
  - Send and receive messages between users
  - Peer-to-peer messaging after login

- **Currency Rates**:
  - View real-time exchange rates from a web service

- **ChatGPT Integration**:
  - Send user messages to ChatGPT and receive intelligent responses
  
- **Interactive GUI**:
  - Built with PyQt5, enhancing user interaction with the platform

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Salman-719/AUBoutique

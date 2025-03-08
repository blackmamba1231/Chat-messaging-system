"""
A client for the healthcare professionals messaging system.

How to run and test:
1. First, start the server: python myserver.py localhost 8090
2. Then start the client: python myclient.py localhost 8090
3. When prompted, enter a username to register with the server
4. Use the following commands to test functionality:
   - send_all <message>: Send a message to all connected users
   - send_to <username> <message>: Send a private message to a specific user
   - list_users: Get a list of all online users
   - exit: Disconnect from the server

For a complete test, run multiple clients in different terminals and test sending
messages between them to verify both broadcast and private messaging functionality.
"""

import sys
import time
from ex2utils import Client

class MessagingClient(Client):
    def __init__(self):
        super().__init__()
        self.registered = False
        self.username = None
        self.last_message = None
        
    def onStart(self):
        print("Connected to server")
        
    def onMessage(self, socket, message):
        # Store the message
        self.last_message = message
        
        # Print the received message
        print(message)
        
        # Check if this is an exit confirmation
        if message == "Client exiting":
            self.stop()
            
        return True
    
    def send_message_to_all(self, message):
        # Send message to all users
        self.send(f"SEND_ALL {message}".encode())
        
    def send_message_to_user(self, username, message):
        # Send private message to a specific user
        self.send(f"SEND_TO {username} {message}".encode())
        
    def list_online_users(self):
        # Request list of online users
        self.send(b"LIST_USERS")
        
    def exit(self):
        # Send exit request to server
        self.send(b"EXIT")

# Parse the IP address and port you wish to connect to
if len(sys.argv) != 3:
    print("Usage: python myclient.py <ip> <port>")
    sys.exit(1)

ip = sys.argv[1]
port = int(sys.argv[2])

# Create and start the client
client = MessagingClient()
client.start(ip, port)

# Register with the server
max_attempts = 5
for attempt in range(max_attempts):
    username = input("Enter your username: ")
    
    # Send registration request
    client.send(f"REGISTER {username}".encode())
    
    # Wait for response
    time.sleep(0.5)
    
    # Check response
    if client.last_message and "Welcome" in client.last_message:
        client.registered = True
        client.username = username
        print(f"Successfully registered as {username}")
        break
    else:
        print("Username already taken or invalid. Try another one.")

if not client.registered:
    print(f"Failed to register after {max_attempts} attempts. Exiting.")
    client.stop()
    sys.exit(1)

# Main client loop
try:
    while True:
        user_input = input("> ")
        
        if user_input.lower() == "exit":
            client.exit()
            break
        elif user_input.lower() == "list_users":
            client.list_online_users()
        elif user_input.lower().startswith("send_all "):
            message = user_input[9:]  # Remove "send_all " prefix
            client.send_message_to_all(message)
        elif user_input.lower().startswith("send_to "):
            # Parse target username and message
            parts = user_input[8:].split(" ", 1)
            if len(parts) == 2:
                target_user, message = parts
                client.send_message_to_user(target_user, message)
            else:
                print("Invalid format. Use: send_to <username> <message>")
        else:
            print("Unknown command. Available commands: send_all, send_to, list_users, exit")
            
except KeyboardInterrupt:
    print("\nExiting...")
    client.exit()
    
# Wait for exit confirmation
time.sleep(1)
print("Client has exited.")

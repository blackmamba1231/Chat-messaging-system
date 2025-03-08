"""
A more robust messaging system for healthcare professionals.
This server acknowledges client connections, messages, and disconnections.
"""

import sys
from ex2utils import Server

class MyServer(Server):
    def onStart(self):
        self.printOutput("Server has started")
        # Initialize client counter
        self.client_count = 0
        # Dictionary to store user information
        self.users = {}
        
    def onConnect(self, socket):
        # Acknowledge new client connection
        self.printOutput("new client connected")
        # Increment client counter
        self.client_count += 1
        # Print active clients count
        self.printOutput(f"{self.client_count} active clients")
        # Set initial state for this client
        socket.registered = False
        
    def onMessage(self, socket, message):
        # Display received message
        self.printOutput(message)
        
        # Parse command and parameters
        parts = message.strip().split(" ", 1)
        command = parts[0].upper()
        parameters = parts[1] if len(parts) > 1 else ""
        
        # Process commands based on protocol
        if command == "REGISTER":
            username = parameters.strip()
            if username and username not in [user["name"] for user in self.users.values()]:
                socket.registered = True
                socket.username = username
                self.users[socket] = {"name": username}
                self.printOutput(f"{username} registered")
                socket.send(f"Welcome {username}!".encode())
            else:
                socket.send(b"Username already taken or invalid")
        elif not socket.registered:
            socket.send(b"not registered")
        elif command == "SEND_ALL":
            if parameters:
                for client in self.users:
                    client.send(f"message from {socket.username}: {parameters}".encode())
            else:
                socket.send(b"Empty message")
        elif command == "SEND_TO":
            parts = parameters.split(" ", 1)
            if len(parts) >= 2:
                target_user = parts[0]
                msg_content = parts[1]
                found = False
                for client in self.users:
                    if self.users[client]["name"] == target_user:
                        client.send(f"message from {socket.username}: {msg_content}".encode())
                        found = True
                        break
                if not found:
                    socket.send(f"User {target_user} not found".encode())
            else:
                socket.send(b"Invalid format. Use: SEND_TO username message")
        elif command == "LIST_USERS":
            user_list = ", ".join([self.users[client]["name"] for client in self.users])
            socket.send(f"Online users: {user_list}".encode())
        elif command == "EXIT":
            socket.send(b"Client exiting")
            return False
        else:
            socket.send(b"unknown command")
            
        return True
        
    def onDisconnect(self, socket):
        # Acknowledge client disconnection
        self.printOutput("a client disconnected")
        # Remove user from users dictionary if registered
        if hasattr(socket, 'registered') and socket.registered:
            if socket in self.users:
                del self.users[socket]
        # Decrement client counter
        self.client_count -= 1
        # Print active clients count
        self.printOutput(f"{self.client_count} active clients")

# Parse the IP address and port you wish to listen on
if len(sys.argv) != 3:
    print("Usage: python myserver.py <ip> <port>")
    sys.exit(1)

ip = sys.argv[1]
port = int(sys.argv[2])

# Create and start the server
server = MyServer()
server.start(ip, port)

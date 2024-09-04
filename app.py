
from simple_websocket_server import WebSocketServer, WebSocket
import threading


SECRET_TOKEN = "your_secret_token"


class AuthWebSocket(WebSocket):
    def handle(self):
        if not hasattr(self, 'authenticated'):
            self.authenticated = False

        if self.data == SECRET_TOKEN:
            self.authenticated = True
            self.send_message("AUTH_SUCCESS")
            print(f"Client {self.address} authenticated successfully")
        elif self.authenticated:
            print(f"Received message from client {self.address}: {self.data}")
            processed_message = self.data # Example processing
            
    def connected(self):
        print(f"New client connected: {self.address}")
        self.send_message("AUTH_REQUIRED")

    def handle_close(self):
        print(f"Client {self.address} disconnected")

server = WebSocketServer('127.0.0.1', 12345, AuthWebSocket)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.start()


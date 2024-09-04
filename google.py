import threading
from simple_websocket_server import WebSocketServer, WebSocket
import re
import emoji
import json
import google.generativeai as genai
from datetime import datetime
from api import send
import pyttsx3
from phone import dail
# Constants
SECRET_TOKEN = "your_secret_token"
WEBSOCKET_HOST = '127.0.0.1'
WEBSOCKET_PORT = 12345

#dail.dial_number()
# AI model configuration
genai.configure(api_key='')

def clean(text):
    text = emoji.replace_emoji(text, '')
    text = re.sub(r'[*%#`]', '', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tts(text, callback=None):
    def run_tts():
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        if callback:
            callback()

    thread = threading.Thread(target=run_tts)
    thread.start()
    return thread

def speak(txt):
    def after_tts():
        print("Broadcasting 'listen^' after TTS")
        AuthWebSocket.broadcast('listen^')

    tts(txt, callback=after_tts)

class AuthWebSocket(WebSocket):
    clients = set()  # Use a set for faster lookup and unique clients

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.authenticated = False
        AuthWebSocket.clients.add(self)

    def handle(self):
        if not self.authenticated:
            if self.data == SECRET_TOKEN:
                self.authenticated = True
                self.send_message("AUTH_SUCCESS")
                print(f"Client {self.address} authenticated successfully")
            return

        print(f"Received message from client {self.address}: {self.data}")
        com_model('user', self.data)

    def connected(self):
        print(f"New client connected: {self.address}")
        self.send_message("AUTH_REQUIRED")

    def handle_close(self):
        print(f"Client {self.address} disconnected")
        AuthWebSocket.clients.remove(self)

    @classmethod
    def broadcast(cls, message):
        for client in cls.clients:
            if client.authenticated:
                msg = clean(message)
                client.send_message(msg)
                if(message != 'listen^'):
                    speak(msg)

# Load system instructions
with open('instruction.txt', 'r', encoding='utf-8') as file:
    sys_ins = file.read()

info = f'For our information date and time now are {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'

# AI model setup
safe = [
    {"category": f"HARM_CATEGORY_{cat}", "threshold": "BLOCK_NONE"}
    for cat in ["HARASSMENT", "HATE_SPEECH", "SEXUALLY_EXPLICIT", "DANGEROUS_CONTENT"]
]

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=sys_ins + info,
    safety_settings=safe
)

chat_session = model.start_chat()

def process(action, data):
    print(f'Processing data: {data}, {action}')
    middleware = send(action, data)
    com_model('middleware', middleware['response_body'])

def com_model(role, msg):
    print(role, msg)
    response = chat_session.send_message(msg)
    
    pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    match = re.search(pattern, response.text)
    
    if match:
        try:
            handle(json.loads(match.group(0)))
        except json.JSONDecodeError as e:
            print(f"Invalid JSON data in the matched content: {e}")
    else:
        print("Model:", response.text)
        AuthWebSocket.broadcast(response.text)

def handle(data):
    print(data)
    for action in ['checkin', 'checkout', 'info', 'payment', 'update', 'room']:
        if action in data:
            process(action, data[action])
            return
    print("No relevant data found in the JSON content.")

def run_websocket_server():
    server = WebSocketServer(WEBSOCKET_HOST, WEBSOCKET_PORT, AuthWebSocket)
    server.serve_forever()

def run_ai_model():
    while True:
        user_input = input("You (text): ")
        com_model('user', user_input)
        if user_input.lower() == "exit":
            break

# Start components
websocket_thread = threading.Thread(target=run_websocket_server)
ai_thread = threading.Thread(target=run_ai_model)

websocket_thread.start()
ai_thread.start()

# Wait for threads to complete
websocket_thread.join()
ai_thread.join()

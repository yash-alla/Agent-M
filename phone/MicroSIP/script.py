import sys
import asyncio
import websockets

SECRET_TOKEN = "your_secret_token"  # Ensure this matches the server's token
WEBSOCKET_HOST = '127.0.0.1'
WEBSOCKET_PORT = 12345

async def send_message(event, caller_id):
    uri = f"ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}"
    async with websockets.connect(uri) as websocket:
        response = await websocket.recv()
        print(f"Initial response: {response}")
        
        if response == "AUTH_REQUIRED":
            print(f"Sending SECRET_TOKEN: {SECRET_TOKEN}")
            await websocket.send(SECRET_TOKEN)
            
        auth_response = await websocket.recv()
        print(f"Auth Response: {auth_response}")

        if auth_response == "AUTH_SUCCESS":
            print('Authenticated successfully')
            message = f"{event}:{caller_id}"
            await websocket.send(message)
            print(f'Sent: {message}')
        else:
            print("Authentication failed.")

def handle_event(event, caller_id):
    asyncio.run(send_message(event, caller_id))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: script.py <event> <caller_id>")
        sys.exit(1)

    event = sys.argv[1]
    caller_id = sys.argv[2]

    handle_event(event, caller_id)

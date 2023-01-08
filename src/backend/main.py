import asyncio
import json

import websockets

async def main():
    # Connect to the websocket server
    uri = "ws://localhost:10001"
    async with websockets.connect(uri) as websocket:
        # Send a message to the server
        message = {"endpoint": "ping", "nonce": 0}
        await websocket.send(json.dumps(message))
        print(f"> {message}")

        # Receive a message from the server
        response = await websocket.recv()
        print(f"< {response}")

# Run the client
asyncio.run(main())

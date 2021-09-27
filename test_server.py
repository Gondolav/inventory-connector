import asyncio
import json
import websockets


async def hello(websocket, path):
    query = {"type": "Bed", "manufacturer": "Bosch", "model": "Med231"}
    await websocket.send(json.dumps(query).encode())
    print(f">>> {query}")

    res = await websocket.recv()
    print(f"<<< {res}")


async def main():
    async with websockets.serve(hello, "localhost", 8765):
        await asyncio.Future()  # run forever


asyncio.run(main())

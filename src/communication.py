from src.models import Item
from typing import Any, Callable, Coroutine, Dict, List
import websockets
import json

from src.translation import Translator


class Response:
    """
    A response to a query to send back to the server.
    """

    def __init__(self, found: bool, items: List[Item]):
        self.found = found
        self.items = items

    def serialize(self) -> dict:
        return {
            "found": self.found,
            "items": list(map(lambda item: item.serialize(), self.items)),
        }


class Request:
    """
    A request sent by the server.
    """

    def __init__(self, connection, translator: Translator, item: Item):
        self._connection = connection
        self._translator = translator
        self.item = item

    async def reply(self, response: Response):
        await self._connection.send(json.dumps(response.serialize()))

    def __repr__(self) -> str:
        return str(self.item)


class Client:
    """
    A client built on top of WebSockets to communicate with the server.
    """

    def __init__(self, server_uri: str, translator: Translator):
        self._uri = server_uri
        self._translator = translator

    async def connect(self):
        async for websocket in websockets.connect(self._uri):
            # Try-except-continue used for automatic reconnection with exponential backoff
            try:
                self._connection = websocket
                async for message in self._connection:
                    # For every new message, decode it and translate it to the client-specific schema
                    json_obj = json.loads(message.decode())
                    item = Item(
                        json_obj["type"], json_obj["manufacturer"], json_obj["model"]
                    )
                    request = Request(self._connection, self._translator, item)
                    await self.on_message_handler(request)
            except websockets.ConnectionClosed:
                continue

    async def close(self):
        await self._connection.close()

    def on_message(self, handler: Callable[[Request], Coroutine[Any, Any, Any]]):
        self.on_message_handler = handler

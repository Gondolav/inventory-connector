import websockets
import json

from typing import Any, Callable, Coroutine, List, Optional
from src.models import Item


class Response:
    """
    A response to a query to send back to the server.
    """

    def __init__(self, found: bool, items: List[Item], price: Optional[float] = None):
        self.found = found
        self.items = items
        self.price = price

    def serialize(self) -> dict:
        """
        Serializes the response to a dictionary.
        """
        d = {
            "found": self.found,
            "items": list(map(lambda item: item.serialize(), self.items)),
        }
        if self.price:
            d["price"] = self.price
        return d

    def __repr__(self) -> str:
        return str(self.serialize())


class Request:
    """
    A request sent by the server.
    """

    def __init__(self, connection, item: Item):
        self._connection = connection
        self.item = item

    async def reply(self, response: Response):
        """
        Answers the request with the given response.
        """
        await self._connection.send(
            json.dumps(response.serialize(), ensure_ascii=False).encode()
        )

    def __repr__(self) -> str:
        return str(self.item)


class Client:
    """
    A client built on top of WebSockets to communicate with the server.
    """

    def __init__(self, server_uri: str):
        self._uri = server_uri

    async def connect(self):
        """
        Connects to the server.
        """
        async for websocket in websockets.connect(self._uri):
            # Try-except-continue used for automatic reconnection with exponential backoff
            try:
                self._connection = websocket
                async for message in self._connection:
                    json_obj = json.loads(message.decode())
                    item = Item(
                        json_obj["type"], json_obj["manufacturer"], json_obj["model"]
                    )
                    request = Request(self._connection, item)
                    await self.on_message_handler(request)
            except websockets.ConnectionClosed:
                continue

    async def close(self):
        """
        Closes the connection to the server.
        """
        await self._connection.close()

    def on_message(self, handler: Callable[[Request], Coroutine[Any, Any, Any]]):
        """
        Registers a message handler.
        """
        self.on_message_handler = handler

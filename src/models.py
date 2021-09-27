from abc import ABC
from typing import Dict, List, Union
from enum import Enum


class Item:
    def __init__(
        self,
        id: str,
        type: str,
        manufacturer: str,
        model: str,
        condition: Union[str, None] = None,
    ):
        self.id = id
        self.type = type
        self.manufacturer = manufacturer
        self.model = model
        self.condition = condition

    @staticmethod
    def deserialize(obj: Dict[str, str]):
        """
        Builds an item given its dictionary representation.
        """
        return Item(obj["type"], obj["manufacturer"], obj["model"], obj["condition"])

    def to_sentence(self) -> str:
        """
        Converts the item into a sentence.
        """
        return f"{self.type} {self.manufacturer} {self.model}"

    def serialize(self) -> Dict[str, str]:
        """
        Serializes the item into a dictionary.
        """
        d = {"type": self.type, "manufacturer": self.manufacturer, "model": self.model}
        if self.condition:
            d["condition"] = self.condition

        if self.id:
            d["id"] = self.id

        return d


class Language(Enum):
    """
    The language used by the client's inventory.
    """

    EN = "en"
    FR = "fr"


class ConnectionType(Enum):
    """
    The connection type.
    """

    DB = "DB"
    API = "API"


class HttpMethod(Enum):
    """
    The HTTP method to use.
    """

    GET = "GET"

    @classmethod
    def values(cls):
        return list(map(lambda c: c.value, cls))


class Endpoint:
    """
    The API Endpoint to use.
    """

    def __init__(
        self,
        path: str,
        method: HttpMethod,
        query_params: Dict[str, str],
        path_params: Dict[str, str],
    ):
        self.path = path
        self.method = method
        self.query_params = query_params
        self.path_params = path_params

        self.has_query_params = len(self.query_params) > 0
        self.has_path_params = len(self.path_params) > 0

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False


class Condition:
    """
    The item's condition field.
    """

    def __init__(self, name: str, allowed_values: List[str]):
        self.name = name
        self.allowed_values = allowed_values

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False


class Fields:
    """
    The item's fields mapping.
    """

    def __init__(
        self, id: str, type: str, manufacturer: str, model: str, condition: Condition
    ):
        self.id = id
        self.type = type
        self.manufacturer = manufacturer
        self.model = model
        self.condition = condition

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False


class Config(ABC):
    """
    A configuration.
    """

    def __init__(
        self,
        id: int,
        type: ConnectionType,
        url: str,
        token: str,
        language: Language,
        fields: Fields,
    ):
        self.id = id
        self.type = type
        self.url = url
        self.token = token
        self.language = language
        self.fields = fields

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False


class DbConfig(Config):
    """
    A configuration for a DB connection.
    """

    def __init__(
        self,
        id: int,
        type: ConnectionType,
        url: str,
        token: str,
        language: Language,
        fields: Fields,
        table: str,
    ):
        super().__init__(id, type, url, token, language, fields)
        self.table = table

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False


class ApiConfig(Config):
    """
    A configuration for an API connection.
    """

    def __init__(
        self,
        id: int,
        type: ConnectionType,
        url: str,
        token: str,
        language: Language,
        fields: Fields,
        endpoint: Endpoint,
    ):
        super().__init__(id, type, url, token, language, fields)
        self.endpoint = endpoint

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

from typing import Any, Dict, List, cast
from src.models import ApiConfig, Config, DbConfig, HttpMethod, Item
from databases import Database
from abc import ABC, abstractmethod
import aiohttp
import re


class Querier(ABC):
    """
    Abstract class modeling a generic service querier.
    """

    def __init__(self, config: Config):
        super().__init__()
        self._config = config

    @abstractmethod
    async def connect(self):
        """
        Connects to the service.
        """
        pass

    @abstractmethod
    async def disconnect(self):
        """
        Disconnects from the service.
        """
        pass

    @abstractmethod
    async def query(self) -> List[Item]:
        """
        Queries the service, returning a list of items.
        """
        pass


class DbQuerier(Querier):
    """
    DB querier. It supports SQLite, PostgreSQL and MySQL.
    """

    def __init__(self, config: Config):
        super().__init__(config)
        self._config = cast(DbConfig, config)
        self._database = Database(config.url)

    async def connect(self):
        print("Connecting to the DB...")
        await self._database.connect()

    async def disconnect(self):
        print("Disconnecting from the DB...")
        await self._database.disconnect()

    def _build_item(self, row: Dict[str, str]) -> Item:
        fields = self._config.fields
        return Item(
            row[fields.type],
            row[fields.manufacturer],
            row[fields.model],
            id=row[fields.id],
        )

    async def query(self) -> List[Item]:
        print("Querying the database...")
        fields = self._config.fields
        fields_string = ", ".join(
            [fields.id, fields.type, fields.manufacturer, fields.model]
        )
        condition = self._config.fields.condition
        condition_string = " OR ".join(
            [
                f"{condition.name} = :{value.replace(' ', '_')}"
                for value in condition.allowed_values
            ]
        )
        return list(
            map(
                self._build_item,
                await self._database.fetch_all(
                    query=f"SELECT {fields_string} FROM {self._config.table} WHERE {condition_string}",
                    values={
                        value.replace(" ", "_"): value
                        for value in condition.allowed_values
                    },
                ),
            )
        )


class ApiQuerier(Querier):
    """
    API querier.
    """

    def __init__(self, config: Config):
        super().__init__(config)
        self._config = cast(ApiConfig, config)
        self._session = aiohttp.ClientSession()

    async def connect(self):
        print("Connecting to the API...")
        pass

    async def disconnect(self):
        print("Disconnecting from the API...")
        await self._session.close()

    def _build_item(self, json: Dict[str, str]) -> Item:
        fields = self._config.fields
        return Item(
            json[fields.type],
            json[fields.manufacturer],
            json[fields.model],
            id=json[fields.id],
        )

    async def query(self) -> List[Item]:
        print("Querying the API...")
        url = self._config.url
        endpoint = self._config.endpoint
        if endpoint.method == HttpMethod.GET:
            path = endpoint.path
            if endpoint.has_path_params:
                path = re.sub(
                    r"/([^/]+)",
                    lambda x: f"/{str(endpoint.path_params[x.group().replace('/', '').replace('{', '').replace('}', '')])}",
                    path,
                )

            # Add to query params one parameter for filtering on the condition of the object
            condition = self._config.fields.condition
            query_params: Dict[str, Any] = endpoint.query_params
            query_params[condition.name] = condition.allowed_values

            async with self._session.get(f"{url}/{path}", params=query_params) as resp:
                json = await resp.json()
                return list(map(self._build_item, json))
        else:
            return []

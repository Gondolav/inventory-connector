from typing import Dict, List, cast
from src.models import ApiConfig, Config, DbConfig, Item
from databases import Database
from abc import ABC, abstractmethod


class Querier(ABC):
    """
    Abstract class modeling a generic service querier.
    """

    def __init__(self, config: Config):
        super().__init__()
        self.config = config

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
            [f"{condition.name} = :{value}" for value in condition.allowed_values]
        )
        return list(
            map(
                self._build_item,
                await self._database.fetch_all(
                    query=f"SELECT {fields_string} FROM {self._config.table} WHERE {condition_string}",
                    values={value: value for value in condition.allowed_values},
                ),
            )
        )


class ApiQuerier(Querier):
    """
    API querier.
    """

    def __init__(self, config: Config):
        super().__init__(config)
        self.config = cast(ApiConfig, config)

    async def connect(self):
        pass

    async def disconnect(self):
        pass

    async def query(self) -> List[Item]:
        print("Querying the API...")
        pass

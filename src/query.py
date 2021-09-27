from typing import List
from src.communication import Request
from src.models import ApiConfig, DbConfig, Item


async def query_db(item: Item, config: DbConfig) -> List[Item]:
    print("Querying the database...")
    table = config.table

    pass


async def query_api(item: Item, config: ApiConfig) -> List[Item]:
    print("Querying the API...")
    pass

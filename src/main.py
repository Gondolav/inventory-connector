import argparse
import asyncio
from src.match import Matcher
from typing import Any, Callable, Coroutine, List
from src.query import ApiQuerier, DbQuerier
from src.models import ConnectionType, Item

from src.translation import Translator
from src.communication import Client, Request, Response
from src.parser import ConfigParser


def parse_args():
    """
    Prepares the argument parser, parses the provided arguments and returns the retrieved information as a tuple.
    """
    parser = argparse.ArgumentParser(description="Inventory connector.")
    parser.add_argument(
        "server_uri", type=str, help="the uri of the server to connect to"
    )
    parser.add_argument("config", type=str, help="the name of the configuration file")
    args = parser.parse_args()
    return args.server_uri, args.config


async def handle_request(
    query_handler: Callable[[], Coroutine[Any, Any, List[Item]]],
    request: Request,
    matcher: Matcher,
):
    print(f"Handling new request {request}...")

    requested_item = request.item
    items: List[Item] = await query_handler()

    if not items:
        print("No items found!")
        await request.reply(Response(False, []))
        return

    matches = matcher.find_matches(requested_item, items)

    if not matches:
        print("No matches found!")
        await request.reply(Response(False, []))
        return

    await request.reply(Response(True, matches))


async def main():
    client = None
    querier = None
    try:
        print("Welcome to the inventory connector!")
        server_uri, config_filename = parse_args()

        print(f"Validating and parsing the configuration file '{config_filename}'...")
        parser = ConfigParser(config_filename)
        config = parser.parse()

        print("Initializing the client...")
        translator = Translator(config.fields)
        client = Client(server_uri, translator)
        matcher = Matcher(config.language)

        querier = (
            DbQuerier(config)
            if config.type == ConnectionType.DB
            else ApiQuerier(config)
        )
        await querier.connect()
        client.on_message(lambda r: handle_request(querier.query, r, matcher))

        print("Connecting to the server...")
        await client.connect()
    except KeyboardInterrupt:
        print("Exiting...")
        if client:
            await client.close()

        if querier:
            await querier.disconnect()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

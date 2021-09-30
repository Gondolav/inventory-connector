# inventory-connector

## Installation

To install the required modules, run:

```bash
pip install -r requirements.txt
```

## Usage

```text
usage: main.py [-h] server_uri config

Inventory connector.

positional arguments:
  server_uri  the uri of the WebSockets server to connect to
  config      the name of the configuration file

optional arguments:
  -h, --help  show this help message and exit
```

From the root of the project, run the connector with:

```bash
python -m src.main <server_ws_uri> <config_file>
```

A trivial example could be:

```bash
python -m src.main ws://localhost:8765 config_file_examples/api_config.json
```

The connector, upon request from the server, will:

1. Convert the request to a format understandable by the client (specified in the configuration file, see below)
2. Get all the items available (from either DB or API, depending on what has been specified in the config)
3. Compute the word embeddings (with [SentenceBERT](https://github.com/UKPLab/sentence-transformers)) for each item and for the query, compute the cosine similarity between each, and filter out all those that have a similarity below 0.6.
4. Send the answer back, converting it to the format understandable by the server

## Configuration files

The configuration file is essential to the connector. It specifies all the required parameters and information for successfully retrieving the data from the source (DB or API).

All fields are mandatory.

### DB configuration file format

```jsonc
{
  "id": 2, // the connector identifier
  "type": "DB", // the connection type to use for retrieving data. Can be either 'DB' or 'API'
  "url": "mysql://sql11440999:xyWbXgFIXC@sql11.freemysqlhosting.net/sql11440999", // the DB URL, as understood by [SQLAlchemy](https://docs.sqlalchemy.org/en/14/core/engines.html)
  "token": "abcdf", // the token to use for communicating with the server
  "language": "fr", // the language of the data retrieved. Can be either 'fr' or 'en'
  "fields": {
    // the name of the fields in the database
    "id": "id", // the primary key id
    "type": "type", // the item's type
    "manufacturer": "brand", // the item's manufacturer
    "model": "model", // the item's model
    "condition": {
      "name": "status", // the item's condition
      "allowedValues": ["disponible", "à disposition"] // only items with these values as condition will be retrieved
    }
  },
  "table": "equipment" // the name of the SQL table to query
}
```

### API configuration file format

```jsonc
{
  "id": 12345, // the connector identifier
  "type": "API", // the connection type to use for retrieving data. Can be either 'DB' or 'API'
  "url": "https://epfl-test.free.beeceptor.com", // the API URL
  "token": "abcdf", // the token to use for communicating with the server
  "language": "fr", // the language of the data retrieved. Can be either 'fr' or 'en'
  "fields": {
    // the name of the fields in the API's underlying database
    "id": "eid", // the primary key id
    "type": "category", // the item's type
    "manufacturer": "manufacturer", // the item's manufacturer
    "model": "model", // the item's model
    "condition": {
      "name": "status", // the item's condition
      "allowedValues": ["available", "disponible"] // only items with these values as condition will be retrieved
    }
  },
  "endpoint": {
    // endpoint information
    "auth": "the auth token", // the token to use for authentication
    "path": "items", // the path of the resource
    "method": "GET", // the HTTP method to use. Can be only 'GET' for now
    "parameters": {
      "query": [], // a list of lists containing two elements. The first one is the name of the query parameter, the second one the value. Can be empty
      "path": [] // a list of lists containing two elements. The first one is the name of the path parameter, the second one the value. Can be empty
    }
  }
}
```

The API has to accept as query parameter for the given endpoint the item's condition (with the name specified in the configuration), so that the data can be correctly filtered.

## Tests

To install the modules required for the tests, run:

```bash
pip install -r requirements_dev.txt
```

Then, to run the tests, execute:

```bash
pytest tests/
```

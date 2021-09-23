# Imports
import json
import os

from enum import Enum
from typing import List, Tuple


class _ConnectionType(Enum):
    DB = "DB"
    API = "API"


class _HttpMethod(Enum):
    GET = "GET"

    @classmethod
    def values(cls):
        return list(map(lambda c: c.value, cls))


class _Endpoint:
    def __init__(
        self,
        path: str,
        method: _HttpMethod,
        query_params: List[Tuple[str, str]],
        path_params: List[Tuple[str, str]],
    ):
        self.path = path
        self.method = method
        self.query_params = query_params
        self.path_params = path_params

        self.has_query_params = len(self.query_params) > 0
        self.has_path_params = len(self.path_params) > 0


class Config:
    def __init__(
        self, id: int, type: _ConnectionType, url: str, token: str, fields: dict
    ):
        self.id = id
        self.type = type
        self.url = url
        self.token = token
        self.fields = fields


class DbConfig(Config):
    def __init__(
        self,
        id: int,
        type: _ConnectionType,
        url: str,
        token: str,
        fields: dict,
        table: str,
    ):
        super().__init__(id, type, url, token, fields)
        self.table = table


class ApiConfig(Config):
    def __init__(
        self,
        id: int,
        type: _ConnectionType,
        url: str,
        token: str,
        fields: dict,
        endpoint: _Endpoint,
    ):
        super().__init__(id, type, url, token, fields)
        self.endpoint = endpoint


class ConfigParser:
    def __init__(self, config_filename: str):
        if os.path.isfile(config_filename):
            with open(config_filename, "r") as config_file:
                config_dict = json.load(config_file)
                valid, error = self._validate(config_dict)
                if valid:
                    self.config = config_dict
                else:
                    print(f"File {config_filename} not valid: {error}")

        else:
            print(f"File {config_filename} does not exist")

    def _validate(self, config: dict) -> Tuple[bool, str]:
        required_keys = ["id", "type", "url", "token", "fields"]
        if all(k in config for k in required_keys):
            if not config["id"]:
                return False, "Empty 'id' field"

            if not config["url"]:
                return False, "Empty 'url' field"

            if not config["token"]:
                return False, "Empty 'token' field"

            fields = config["fields"]
            if not fields:
                return False, "Empty 'fields' field"

            required__fields_keys = [""]  # TODO:
            if all(k in fields for k in required__fields_keys):
                type = config["type"]
                if type == "DB":
                    if "table" not in config:
                        return False, "Key 'table' is missing"

                    table = config["table"]
                    if not table:
                        return False, "Empty 'table' field"
                elif type == "API":
                    if "endpoint" not in config:
                        return False, "Key 'endpoint' is missing"

                    endpoint = config["endpoint"]
                    if not endpoint:
                        return False, "Empty 'endpoint' field"

                    required_endpoint_keys = ["path", "method", "parameters"]
                    if all(k in endpoint for k in required_endpoint_keys):
                        if not endpoint["path"]:
                            return False, "Empty 'path' field"

                        method = endpoint["method"]
                        if not method:
                            return False, "Empty 'method' field"

                        if method not in _HttpMethod.values():
                            return False, f"Unknown 'method' value: {method}"

                        parameters = endpoint["parameters"]
                        required_parameters_keys = ["query", "path"]
                        if all(k in endpoint for k in required_parameters_keys):
                            if not parameters["query"]:
                                return False, f"Empty 'query' field"

                            path_params = parameters["path"]
                            if not path_params:
                                return (
                                    False,
                                    f"Empty 'path' field in endpoint parameters",
                                )

                            if not all(
                                p_value and "{" + p_name + "}" in endpoint["path"]
                                for p_name, p_value in path_params
                            ):
                                return False, f"Empty or unknown path parameter"
                        else:
                            return (
                                False,
                                f"One of the required keys {required_parameters_keys} is missing in 'parameters'",
                            )
                    else:
                        return (
                            False,
                            f"One of the required keys {required_endpoint_keys} is missing in 'endpoint'",
                        )
                else:
                    return False, f"Unknown 'type' value: {type}"
            else:
                return (
                    False,
                    f"One of the required keys {required__fields_keys} is missing in 'fields'",
                )
        else:
            return False, f"One of the required keys {required_keys} is missing"

    def parse(self) -> Config:
        id = self.config["id"]
        type = _ConnectionType[self.config["type"]]
        url = self.config["url"]
        token = self.config["token"]
        fields = self.config["fields"]

        if type == "DB":
            table = self.config["table"]
            return DbConfig(id, type, url, token, fields, table)
        else:
            endpoint_dict = self.config["endpoint"]
            params_dict = endpoint_dict["parameters"]
            endpoint = _Endpoint(
                endpoint_dict["path"],
                _HttpMethod[endpoint_dict["method"]],
                params_dict["query"],
                params_dict["path"],
            )
            return ApiConfig(id, type, url, token, fields, endpoint)

import json
import os
import re
from src.models import (
    ApiConfig,
    Condition,
    Config,
    ConnectionType,
    DbConfig,
    Endpoint,
    Fields,
    HttpMethod,
    Language,
)

from typing import Tuple


class ParserException(Exception):
    """
    A parser exception.
    """


class ConfigParser:
    """
    A configuration file parser. It validates the file on initialization.
    """

    def __init__(self, config_filename: str):
        if os.path.isfile(config_filename):
            with open(config_filename, "r") as config_file:
                config_dict = json.load(config_file)
                valid, error = self._validate(config_dict)
                if valid:
                    self.config = config_dict
                else:
                    raise ParserException(f"File {config_filename} not valid: {error}")

        else:
            raise ParserException(f"File {config_filename} does not exist")

    def _validate(self, config: dict) -> Tuple[bool, str]:
        def remove_braces(s: str) -> str:
            s = s.replace("{", "")
            s = s.replace("}", "")
            return s

        required_keys = ["id", "type", "url", "token", "language", "fields"]
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

            required_fields_keys = [
                "id",
                "type",
                "manufacturer",
                "model",
                "condition",
            ]
            if all(k in fields for k in required_fields_keys):
                condition = fields["condition"]
                if not condition:
                    return False, "Empty 'condition' field"

                if "name" not in condition or "allowedValues" not in condition:
                    return (
                        False,
                        f"One of the required keys [name, allowedValues] is missing in 'condition'",
                    )

                if not condition["name"]:
                    return False, "Empty 'name' field"

                if not condition["allowedValues"]:
                    return False, "Empty 'allowedValues' field"

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

                    required_endpoint_keys = ["auth", "path", "method", "parameters"]
                    if all(k in endpoint for k in required_endpoint_keys):
                        if not endpoint["auth"]:
                            return False, "Empty 'auth' field"

                        endpoint_path = endpoint["path"]
                        if not endpoint_path:
                            return False, "Empty 'path' field"

                        method = endpoint["method"]
                        if not method:
                            return False, "Empty 'method' field"

                        if method not in HttpMethod.values():
                            return False, f"Unknown 'method' value: {method}"

                        parameters = endpoint["parameters"]
                        required_parameters_keys = ["query", "path"]
                        if all(k in parameters for k in required_parameters_keys):
                            path_params = parameters["path"]

                            # Verify that all path parameters specified are provided
                            path_params_in_url = list(
                                map(
                                    lambda m: remove_braces(m),
                                    re.findall(r"/([^/]+)", endpoint_path),
                                )
                            )
                            if not all(
                                p in dict(path_params) for p in path_params_in_url
                            ):
                                return (
                                    False,
                                    f"Path parameter in url not found in specified parameters",
                                )

                            # Verify that all path parameters provided are used in the path
                            if path_params and not all(
                                param[1] and "{" + param[0] + "}" in endpoint_path
                                for param in path_params
                            ):
                                return False, f"Empty or unused path parameter in url"
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
                    f"One of the required keys {required_fields_keys} is missing in 'fields'",
                )
        else:
            return False, f"One of the required keys {required_keys} is missing"

        return True, "Valid"

    def parse(self) -> Config:
        """
        Parses the file, returning the corresponding configuration.
        """
        id = self.config["id"]
        type = ConnectionType[self.config["type"]]
        url = self.config["url"]
        token = self.config["token"]
        language = Language[self.config["language"].upper()]
        fields = self.config["fields"]

        condition = fields["condition"]
        fields = Fields(
            fields["id"],
            fields["type"],
            fields["manufacturer"],
            fields["model"],
            Condition(condition["name"], condition["allowedValues"]),
        )

        if type == ConnectionType.DB:
            table = self.config["table"]
            return DbConfig(id, type, url, token, language, fields, table)
        else:
            endpoint_dict = self.config["endpoint"]
            params_dict = endpoint_dict["parameters"]
            endpoint = Endpoint(
                endpoint_dict["auth"],
                endpoint_dict["path"],
                HttpMethod[endpoint_dict["method"]],
                dict(params_dict["query"]),
                dict(params_dict["path"]),
            )
            return ApiConfig(id, type, url, token, language, fields, endpoint)

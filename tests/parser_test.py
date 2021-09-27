from src.models import (
    ApiConfig,
    Condition,
    ConnectionType,
    DbConfig,
    Endpoint,
    Fields,
    HttpMethod,
    Language,
)
from src.parser import ConfigParser, ParserException
import pytest
from typing import cast

CONFIGS_PATH = "tests/configs"


def test_parser_parses_db_config():
    parser = ConfigParser(f"{CONFIGS_PATH}/db_config.json")
    config: DbConfig = cast(DbConfig, parser.parse())

    assert config.id == 12345, "Wrong id"
    assert config.type == ConnectionType.DB, "Wrong connection type"
    assert config.url == "an url", "Wrong url"
    assert config.token == "abcdf", "Wrong token"
    assert config.language == Language.FR, "Wrong language"
    assert config.fields == Fields(
        "eid",
        "category",
        "manufacturer",
        "model",
        Condition("status", ["available", "disponible"]),
    ), "Wrong fields"
    assert config.table == "items"


def test_parser_parses_api_config():
    parser = ConfigParser(f"{CONFIGS_PATH}/api_config.json")
    config: ApiConfig = cast(ApiConfig, parser.parse())

    assert config.id == 12345, "Wrong id"
    assert config.type == ConnectionType.API, "Wrong connection type"
    assert config.url == "an url", "Wrong url"
    assert config.token == "abcdf", "Wrong token"
    assert config.language == Language.EN, "Wrong language"
    assert config.fields == Fields(
        "eid",
        "category",
        "manufacturer",
        "model",
        Condition("status", ["available", "disponible"]),
    ), "Wrong fields"
    assert config.endpoint == Endpoint(
        "items/{id}/{param}",
        HttpMethod.GET,
        {"model": "gt", "type": "bed"},
        {"id": "abc", "param": "value"},
    )


def test_parser_id_not_found():
    with pytest.raises(ParserException):
        ConfigParser(f"{CONFIGS_PATH}/no_id.json")


def test_parser_language_not_found():
    with pytest.raises(ParserException):
        ConfigParser(f"{CONFIGS_PATH}/no_language.json")


def test_parser_type_not_found():
    with pytest.raises(ParserException):
        ConfigParser(f"{CONFIGS_PATH}/no_type.json")


def test_parser_url_not_found():
    with pytest.raises(ParserException):
        ConfigParser(f"{CONFIGS_PATH}/no_url.json")


def test_parser_token_not_found():
    with pytest.raises(ParserException):
        ConfigParser(f"{CONFIGS_PATH}/no_token.json")


def test_parser_fields_not_found():
    with pytest.raises(ParserException):
        ConfigParser(f"{CONFIGS_PATH}/no_fields.json")


def test_parser_db_table_not_found():
    with pytest.raises(ParserException):
        ConfigParser(f"{CONFIGS_PATH}/no_table.json")


def test_parser_api_endpoint_not_found():
    with pytest.raises(ParserException):
        ConfigParser(f"{CONFIGS_PATH}/no_endpoint.json")


def test_parser_fields_id_not_found():
    with pytest.raises(ParserException):
        ConfigParser(f"{CONFIGS_PATH}/no_fields_id.json")


def test_parser_fields_type_not_found():
    with pytest.raises(ParserException):
        ConfigParser(f"{CONFIGS_PATH}/no_fields_type.json")


def test_parser_fields_manufacturer_not_found():
    with pytest.raises(ParserException):
        ConfigParser(f"{CONFIGS_PATH}/no_fields_manufacturer.json")


def test_parser_fields_model_not_found():
    with pytest.raises(ParserException):
        ConfigParser(f"{CONFIGS_PATH}/no_fields_model.json")


def test_parser_fields_condition_not_found():
    with pytest.raises(ParserException):
        ConfigParser(f"{CONFIGS_PATH}/no_fields_condition.json")


def test_parser_fields_condition_name_not_found():
    with pytest.raises(ParserException):
        ConfigParser(f"{CONFIGS_PATH}/no_fields_condition_name.json")


def test_parser_fields_condition_allowed_values_not_found():
    with pytest.raises(ParserException):
        ConfigParser(f"{CONFIGS_PATH}/no_fields_condition_allowed_values.json")


def test_parser_endpoint_path_not_found():
    with pytest.raises(ParserException):
        ConfigParser(f"{CONFIGS_PATH}/no_endpoint_path.json")


def test_parser_endpoint_method_not_found():
    with pytest.raises(ParserException):
        ConfigParser(f"{CONFIGS_PATH}/no_endpoint_method.json")


def test_parser_endpoint_parameters_not_found():
    with pytest.raises(ParserException):
        ConfigParser(f"{CONFIGS_PATH}/no_endpoint_parameters.json")


def test_parser_endpoint_parameters_path_not_found():
    with pytest.raises(ParserException):
        ConfigParser(f"{CONFIGS_PATH}/no_endpoint_parameters_path.json")


def test_parser_endpoint_parameters_query_not_found():
    with pytest.raises(ParserException):
        ConfigParser(f"{CONFIGS_PATH}/no_endpoint_parameters_query.json")


def test_parser_endpoint_path_param_in_url_not_found():
    with pytest.raises(ParserException):
        ConfigParser(f"{CONFIGS_PATH}/no_path_param_in_url_found.json")


def test_parser_endpoint_path_param_not_found_in_url():
    with pytest.raises(ParserException):
        ConfigParser(f"{CONFIGS_PATH}/no_path_param_found_in_url.json")

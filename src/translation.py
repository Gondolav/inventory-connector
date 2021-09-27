from src.models import Fields
from typing import Dict


class Translator:
    """
    A translator between standard and client-specific schema.
    """

    def __init__(self, fields: Fields):
        self._from_standard_mapping = {}
        self._from_standard_mapping["id"] = fields.id
        self._from_standard_mapping["type"] = fields.type
        self._from_standard_mapping["manufacturer"] = fields.manufacturer
        self._from_standard_mapping["model"] = fields.model
        self._from_standard_mapping["condition"] = fields.condition.name

        self._to_standard_mapping = {}
        self._to_standard_mapping[fields.id] = "id"
        self._to_standard_mapping[fields.type] = "type"
        self._to_standard_mapping[fields.manufacturer] = "manufacturer"
        self._to_standard_mapping[fields.model] = "model"
        self._to_standard_mapping[fields.condition.name] = "condition"

    def from_standard(self, json_obj: Dict[str, str]) -> Dict[str, str]:
        """
        Converts a message using the standard schema to the client-specific schema.
        """
        return {
            self._from_standard_mapping[key]: value for key, value in json_obj.items()
        }

    def to_standard(self, json_obj: Dict[str, str]) -> Dict[str, str]:
        """
        Converts a message using the client-specific schema to the standard schema.
        """
        return {
            self._to_standard_mapping[key]: value for key, value in json_obj.items()
        }

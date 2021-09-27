from src.translation import Translator
from src.models import Condition, Fields


def test_translation_from_standard():
    fields = Fields(
        "idn", "category", "brand", "model", Condition("status", ["available"])
    )
    translator = Translator(fields)

    msg = {
        "id": 123,
        "type": "Car",
        "manufacturer": "Ferrari",
        "model": "GT",
        "condition": "available",
    }

    expected = {
        "idn": msg["id"],
        "category": msg["type"],
        "brand": msg["manufacturer"],
        "model": msg["model"],
        "status": msg["condition"],
    }

    assert expected == translator.from_standard(msg), "The translation is wrong"


def test_translation_to_standard():
    fields = Fields(
        "idn", "category", "brand", "model", Condition("status", ["available"])
    )
    translator = Translator(fields)

    msg = {
        "idn": 123,
        "category": "Car",
        "brand": "Ferrari",
        "model": "GT",
        "status": "available",
    }

    expected = {
        "id": msg["idn"],
        "type": msg["category"],
        "manufacturer": msg["brand"],
        "model": msg["model"],
        "condition": msg["status"],
    }

    assert expected == translator.to_standard(msg), "The translation is wrong"

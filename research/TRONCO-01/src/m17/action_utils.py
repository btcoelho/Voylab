"""Small stdlib-only helpers for parsing model actions."""
import json


def first_json_object(text):
    """Decode the first complete JSON object, allowing nested location objects."""
    decoder = json.JSONDecoder()
    for start, char in enumerate(text):
        if char != "{":
            continue
        try:
            value, _ = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return None

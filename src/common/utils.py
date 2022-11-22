# stdlib
from secrets import token_hex


def generate_random_string() -> str:
    return token_hex(6)

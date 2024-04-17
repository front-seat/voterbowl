import secrets
import string

DEFAULT_ALPHABET = string.ascii_letters + string.digits


def make_token(length: int, alphabet: str = DEFAULT_ALPHABET) -> str:
    """Generate a random token."""
    return "".join(secrets.choice(alphabet) for _ in range(length))

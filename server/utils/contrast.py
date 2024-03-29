import typing as t

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

HEX_COLOR_REGEX = r"^#[0-9a-fA-F]{6}$"


HEX_COLOR_VALIDATOR = RegexValidator(
    HEX_COLOR_REGEX,
    "Enter a valid hex color, like #000000.",
)


def is_valid_hex_color(hex_color: str) -> bool:
    """Return whether the given hex color is valid."""
    try:
        HEX_COLOR_VALIDATOR(hex_color)
        return True
    except ValidationError:
        return False


def get_text_color(bg_hex_color: str) -> t.Literal["black", "white"]:
    """Return an ideal text color for the given background hex color."""
    if not is_valid_hex_color(bg_hex_color):
        raise ValueError("Invalid hex color.")
    hex = bg_hex_color.lstrip("#")
    r = int(hex[:2], 16)
    g = int(hex[2:4], 16)
    b = int(hex[4:], 16)
    yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000
    return "black" if yiq >= 128 else "white"

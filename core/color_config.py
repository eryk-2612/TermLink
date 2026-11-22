"""Load the optional base color for the terminal interface."""

import curses
import json

from core.constants import Others


def load_color_pairs():
    """Return the configured foreground/background pair and its inverse."""
    foreground_name, background_name = "white", "black"
    try:
        with Others.CONFIG_PATH.open(encoding="utf-8") as config_file:
            config = json.load(config_file)
        if isinstance(config, dict):
            foreground_name = _color_name(config.get("foreground"), foreground_name)
            background_name = _color_name(config.get("background"), background_name)
    except (OSError, json.JSONDecodeError):
        pass

    foreground = getattr(curses, f"COLOR_{foreground_name.upper()}")
    background = getattr(curses, f"COLOR_{background_name.upper()}")
    return {
        "default": (foreground, background),
        "selected": (background, foreground),
    }


def _color_name(value, fallback):
    if isinstance(value, str):
        candidate = value.strip().upper()
        if isinstance(getattr(curses, f"COLOR_{candidate}", None), int):
            return candidate.lower()
    return fallback

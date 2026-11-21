import sys
from pathlib import Path


if getattr(sys, "frozen", False):
    _DEFAULT_APP_ROOT = Path(sys.executable).resolve().parent
else:
    _DEFAULT_APP_ROOT = Path(__file__).resolve().parent.parent

# Runtime content stays external and optional; support both beside the app and cwd.
_WORKING_ROOT = Path.cwd()
_APP_ROOT = next(
    (
        root for root in (_DEFAULT_APP_ROOT, _WORKING_ROOT)
        if (root / "data").is_dir() or (root / "locales").is_dir()
    ),
    _DEFAULT_APP_ROOT,
)


class Others:
    DATA_PATH = str(_APP_ROOT / "data") + "/"
    TIMEOUT = 300
    SCREEN_PADDING = 1
    SCROLLBAR_PADDING = 2
    BORDER_PADDING = 2
    CODE_PLACEHOLDER = "_"
    MINIMUM_ENTRIES = 2
    MAXIMUM_ENTRIES = MINIMUM_ENTRIES # currently not recommended to change
    MINIMUM_CATEGORIES = 4 # <0 = add empty boxes until max | 0 = dont add empty boxes | n = add empty boxes until n
    MAXIMUM_CATEGORIES = 4 #  <=0 = no max | n = scroll when more than n

class Colors:
    DEFAULT     = 1
    SELECTED    = 2

class TermTypes:
    EXPLORER    = "explorer"
    CHAT        = "chat"

class EntryTypes:
    TEXT    = "text"
    SWITCH  = "switch"
    BUTTON  = "button"
    AUDIO   = "audio"
    QUIT    = "quit"

class Focus:
    ENTRIES     = "entries"
    CATEGORIES  = "categories"
    CONTENT     = "content"
    LOCK        = "lock"
    INPUT       = "input"

class Popups:
    MSG     = "msg"
    LOCK    = "lock"

class Screens:
    SIGNIN      = "signin"
    BOOT        = "boot"
    EXPLORER    = "explorer"
    FULLSCREEN  = "fullscreen"
    CHAT        = "chat"

class Events:
    CLOSE_ENTRY         = "close_entry"
    OPEN_ENTRY          = "open_entry"
    OPEN_CATEGORY       = "open_category"
    CLOSE_CATEGORY      = "close_category"
    CANCEL              = "cancel"
    SIGNIN              = "signin"
    QUIT                = "quit"
    SEND_REQUEST        = "request"

import json
from pathlib import Path

class Tokens:
    """English defaults, overridden by locales/tokens.json when available."""

    COPYRIGHT = "(C) Terminal Systems"
    MSG_SUCCESS = "Access granted"
    MSG_FAIL = "Access denied"
    FOLDER = "Folder"
    FILES = "Files"
    LEAVE = "Leave"
    TERM_UNNAMED = "Unnamed terminal"
    ERROR = "Error"
    STATES = ["On", "Off"]
    VERBS = ["Turn on", "Turn off"]
    MESSAGE = "Activated"
    PASSCODE = "Enter Passcode"
    PLAYING = "Playing"
    PAUSED = "Paused"
    FLOPPY_INSERTED = "Loading floppy disk..."
    FLOPPY_LOADED = "Floppy disk loaded"
    FLOPPY_REMOVED = "Floppy disk removed"
    LOAD_FROM_DISK = "Load from floppy disk"
    MAIN_MENU = "Main menu"
    MENU_HINT = "UP/DOWN NAVIGATE  ENTER SELECT"
    EXPLORER_HINT = "UP/DOWN NAVIGATE  ENTER OPEN  ESC BACK"
    CHAT_HINT = "ENTER SEND  UP/DOWN SCROLL  ESC EXIT"
    INSERT_FLOPPY = "Insert a floppy disk"
    FLOPPY_READING = "Reading data from floppy disk..."
    FLOPPY_NO_TERMINAL = "No data found"
    FLOPPY_READ_ERROR = "Could not read program"
    FLOPPY_SELECT_TERMINAL = "Select a program"
    SIGNIN = [
        "                                        ",
        "   ▗▄▄▖▗▄▄▄▖ ▗▄▄▖▗▖  ▗▖    ▗▄▄▄▖▗▖  ▗▖  ",
        "  ▐▌     █  ▐▌   ▐▛▚▖▐▌      █  ▐▛▚▖▐▌  ",
        "   ▝▀▚▖  █  ▐▌▝▜▌▐▌ ▝▜▌      █  ▐▌ ▝▜▌  ",
        "  ▗▄▄▞▘▗▄█▄▖▝▚▄▞▘▐▌  ▐▌    ▗▄█▄▖▐▌  ▐▌  ",
        "                                        ",
    ]
    LOGO = [
        "  ______                    __    _       __  ",
        " /_  __/__  _________ ___  / /   (_)___  / /__",
        "  / / / _ \/ ___/ __ \`__\/ /   / / __ \/ //_/",
        " / / /  __/ /  / / / / / / /___/ / / / / ,<   ",
        "/_/  \___/_/  /_/ /_/ /_/_____/_/_/ /_/_/|_|  ",
        "                           by Terminal Systems",
    ]

    @staticmethod
    def _load_tokens():
        path = _APP_ROOT / "locales" / "tokens.json"
        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
            for key, value in data.items():
                setattr(Tokens, key.upper(), value)
        except (OSError, json.JSONDecodeError):
            # Keep the defaults above if the locale file is missing or invalid.
            pass

Tokens._load_tokens()

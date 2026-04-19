
class Files:
    AUDIO_PATH = "data/audio/"

class Colors:
    DEFAULT = 1
    INVERTED = 2
    WARNING = 3
    SELECTED = 4
    TEXT = 5
    OPEN = 6

class TermTypes:
    CHAT        = "chat"
    EXPLORER    = "explorer"

class EntryTypes:
    TEXT    = "text"
    SWITCH  = "switch"
    AUDIO   = "audio"
    LOST    = "lost"
    QUIT    = "quit"

class Focus:
    CONTENT     = "content"
    ENTRIES     = "entries"
    CATEGORIES  = "categories"
    LOCK        = "lock"

class Screens:
    SIGNIN      = "signin"
    BOOT        = "boot"
    TERMINAL    = "terminal"

class Events:
    CLOSE_ENTRY     = "close_entry"
    OPEN_ENTRY      = "open_entry"
    OPEN_CATEGORY   = "open_category"
    CLOSE_CATEGORY  = "close_category"
    SCROLL          = "scroll"
    RETRY_LOCK      = "retry_lock"
    CANCEL_LOCK     = "cancel_lock"
    SWITCH          = "switch"
    GET_RESPONSE    = "response"
    SEND_REQUEST    = "request"
    AUDIO           = "audio"
    BOOT            = "boot"
    SIGNIN          = "signin"
    INIT            = "init"

class TokensDE:
    MSG_SUCCESS     = "Zugriff gewährt"
    MSG_FAIL        = "Zugriff verweigert"
    LOST            = "[FEHLER] Kritischer Datenverlust"
    FOLDER          = "Ordner"
    FILES           = "Dateien"
    LEAVE           = "Verlassen"
    TERM_UNNAMED    = "Unbenanntes Terminal"
    ERROR           = "Fehler"
    STATES          = ["An", "Aus"]
    CAPTIONS        = ["Anschalten", "Ausschalten"]
    PASSCODE        = "Zugangscode"
    SIGNINDE        = [
        r"                                              ",
        r"  ▗▄▖ ▗▖  ▗▖▗▖  ▗▖▗▄▄▄▖▗▖   ▗▄▄▄  ▗▄▄▄▖▗▖  ▗▖ ",
        r" ▐▌ ▐▌▐▛▚▖▐▌▐▛▚▞▜▌▐▌   ▐▌   ▐▌  █ ▐▌   ▐▛▚▖▐▌ ",
        r" ▐▛▀▜▌▐▌ ▝▜▌▐▌  ▐▌▐▛▀▀▘▐▌   ▐▌  █ ▐▛▀▀▘▐▌ ▝▜▌ ",
        r" ▐▌ ▐▌▐▌  ▐▌▐▌  ▐▌▐▙▄▄▖▐▙▄▄▖▐▙▄▄▀ ▐▙▄▄▖▐▌  ▐▌ ",
        r"                                              "
    ]

class Logo:
    DEFAULT         = [
        r"  ______                    __    _       __  ",
        r" /_  __/__  _________ ___  / /   (_)___  / /__",
        r"  / / / _ \/ ___/ __ \`__\/ /   / / __ \/ //_/",
        r" / / /  __/ /  / / / / / / /___/ / / / / ,<   ",
        r"/_/  \___/_/  /_/ /_/ /_/_____/_/_/ /_/_/|_|  ",
        r"                           by Terminal Systems"
    ]


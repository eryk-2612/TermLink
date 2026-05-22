
class Others:
    AUDIO_PATH = "data/audio/"
    TIMEOUT = 300
    COPYRIGHT  = "(C) Terminal Systems"
    SCREEN_PADDING = 1
    SCROLLBAR_PADDING = 2
    BORDER_PADDING = 2
    CODE_PLACEHOLDER = "_"
    MINIMUM_ENTRIES = 2
    MAXIMUM_ENTRIES = 2 # 0 = unlimited
    MINIMUM_CATEGORIES = 4
    MAXIMUM_CATEGORIES = -1 # 0 = unlimited | <0 = no additional boxes

class Colors:
    DEFAULT     = 1
    SELECTED    = 2

class TermTypes:
    EXPLORER    = "explorer"

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

class Popups:
    MSG     = "msg"
    LOCK    = "lock"

class Screens:
    SIGNIN      = "signin"
    BOOT        = "boot"
    TERMINAL    = "terminal"

class Events:
    CLOSE_ENTRY         = "close_entry"
    OPEN_ENTRY          = "open_entry"
    OPEN_CATEGORY       = "open_category"
    CLOSE_CATEGORY      = "close_category"
    CANCEL              = "cancel"
    SIGNIN              = "signin"
    QUIT                = "quit"

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
    SIGNIN          = [
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



class Others:
    AUDIO_PATH = "data/audio/"
    TIMEOUT = 300
    COPYRIGHT  = "(C) Terminal Systems"
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
    VERBS           = ["Anschalten", "Ausschalten"]
    MESSAGE         = "Aktiviert"
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


from .terminal_model import TerminalModel
from core import Others, TokensDE, EntryTypes, get_audio_length

class ExplorerModel(TerminalModel):
    def __init__(self, name, unlock_code=None, categories=None):
        super().__init__(name, unlock_code)
        self._categories = categories or []

    @property
    def categories(self):
        return self._categories

    @categories.setter
    def categories(self, value):
        self._categories = value

class EntryModel:
    def __init__(
        self,
        title=None,
        type=None,
        lines=None,
        unlock_code=None,
        default_state=False,
        current_state=None,
        state_strings=None,
        caption_strings=None,
        audio=None
    ):
        self._title = title
        self._type = type or EntryTypes.LOST
        self._lines = lines or []
        self._unlock_code = unlock_code
        self._default_state = default_state
        self._current_state = default_state
        self._state_strings = state_strings or TokensDE.STATES
        self._caption_strings = caption_strings or TokensDE.CAPTIONS
        self._lock = bool(self._unlock_code)

        self._audio = audio
        self._is_playing = False
        self._audio_length = 0
        self._audio_start_time = 0

        if audio:
            self._audio_length = get_audio_length(Others.AUDIO_PATH + audio)

    @property
    def is_playing(self):
        return self._is_playing

    @is_playing.setter
    def is_playing(self, value):
        self._is_playing = value

    @property
    def audio_start_time(self):
        return self._audio_start_time

    @audio_start_time.setter
    def audio_start_time(self, value):
        self._audio_start_time = value

    @property
    def audio_length(self):
        return self._audio_length

    @property
    def title(self):
        if self._title:
            return self._title
        else :
            return TokensDE.ERROR

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, value):
        self._current_state = value

    @property
    def audio(self):
        return self._audio

    @audio.setter
    def audio(self, value):
        self._audio = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def lines(self):
        return self._lines

    @lines.setter
    def lines(self, value):
        self._lines = value

    @property
    def lock(self):
        return self._lock

    @property
    def unlock_code(self):
        return self._unlock_code

    @unlock_code.setter
    def unlock_code(self, value):
        self._unlock_code = value

    def unlock(self):
        self._lock = False

    def reset_lock(self):
        self._lock = bool(self._unlock_code)

    @property
    def default_state(self):
        return self._default_state

    @default_state.setter
    def default_state(self, value):
        self._default_state = value

    @property
    def state_strings(self):
        return self._state_strings

    @state_strings.setter
    def state_strings(self, value):
        self._state_strings = value

    @property
    def caption_strings(self):
        return self._caption_strings

    @caption_strings.setter
    def caption_strings(self, value):
        self._caption_strings = value

class CategoryModel:
    def __init__(self, title, entries=None, quit=False):
        self._title = title
        self._entries = entries or []
        self._quit = quit

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def quit(self):
        return self._quit

    @quit.setter
    def quit(self, value):
        self._quit = value

    @property
    def entries(self):
        return self._entries

    @entries.setter
    def entries(self, value):
        self._entries = value

from .terminal_model import TerminalModel
from core import Others, Tokens, EntryTypes, get_audio_length

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
        state_labels=None,
        action_verbs=None,
        audio=None,
        message=None
    ):
        self._title = title
        self._type = type
        self._lines = lines or []
        self._unlock_code = unlock_code
        self._default_state = default_state
        self._current_state = default_state
        self._state_labels = state_labels or Tokens.STATES
        self._action_verbs = action_verbs or Tokens.VERBS
        self._message = message or Tokens.MESSAGE
        self._lock = bool(self._unlock_code)

        self._audio = audio
        self._audio_length = 0
        self._audio_start_time = 0
        self._is_playing = False

        if audio:
            self._audio_length = get_audio_length(Others.DATA_PATH + audio)

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
    def is_playing(self):
        return self._is_playing

    @is_playing.setter
    def is_playing(self, value):
        self._is_playing = value

    @property
    def title(self):
        if self._title:
            if self.type == EntryTypes.AUDIO:
                if self.is_playing:
                    return "■ " + self._title
                else:
                    return "▶ " + self._title
            else:
                return self._title
        else :
            return Tokens.ERROR

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
    def locked(self):
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

    @property
    def state_labels(self):
        return self._state_labels

    @state_labels.setter
    def state_labels(self, value):
        self._state_labels = value

    @property
    def action_verbs(self):
        return self._action_verbs

    @action_verbs.setter
    def action_verbs(self, value):
        self._action_verbs = value

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value

class CategoryModel:
    def __init__(self, title, entries=None):
        self._title = title
        self._entries = entries or []

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def entries(self):
        return self._entries

    @entries.setter
    def entries(self, value):
        self._entries = value

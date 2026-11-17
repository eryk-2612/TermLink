class TerminalModel:
    def __init__(self, name = "", unlock_code=None, skip_signin=False):
        self._name = name
        self._unlock_code = unlock_code
        self._lock = bool(self._unlock_code)
        self._skip_signin = skip_signin is True

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def locked(self):
        return self._lock

    def unlock(self):
        self._lock = False

    def reset_lock(self):
        self._lock = bool(self._unlock_code)

    @property
    def skip_signin(self):
        return self._skip_signin

    @skip_signin.setter
    def skip_signin(self, value):
        self._skip_signin = value is True

    @property
    def unlock_code(self):
        return self._unlock_code

    @unlock_code.setter
    def unlock_code(self, value):
        self._unlock_code = value

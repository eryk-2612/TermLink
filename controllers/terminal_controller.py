from core import Focus

class TerminalController:
    def __init__(self, stdscr, model, view, state):
        self.model = model
        self._stdscr = stdscr
        self.view = view
        self.state = state

    def get_input(self):
        return self._stdscr.getch()

    def unlock(self):
        while self.model.lock:
            self.state.focus = Focus.LOCK


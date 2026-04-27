from core import Events, Logo, TokensDE, Focus, Screens, Colors, Others
import curses

class TerminalController:
    def __init__(self, stdscr, model, view, state):
        self.model = model
        self._stdscr = stdscr
        self.view = view
        self.state = state

    def get_input(self, window):
        if window:
            return window.win.getch()
        else:
            return None

    def get_focus_window(self):
        return self.view.get_window(self.state.focus)

    def init_state(self):
        self.state.running = True
        self.state.screen = Screens.SIGNIN
        self.state.event = Events.SIGNIN
        self.state.focus = Focus.SIGNIN

    def run(self):
        self.init_state()
        while self.state.running:
            self.handle_input()
            self.update_state()
            self.draw_view()

    def update_state(self):
        pass

    def continue_signin(self):
        self.state.event = Events.CONTINUE
        self.state.focus = Focus.BOOT
        self.state.screen = Screens.BOOT

    def unlock_terminal(self, entered_code):
        if entered_code == self.model.unlock_code:
            self.state.event = Events.TERM_LOCK_SUC
        else:
            self.state.event = Events.TERM_LOCK_FAIL
        self.state.focus_window = self.view.get_window()
        self.state.focus = Focus.BOOT

    def enter_code(self, entered_code, key):
        if len(entered_code) < len(self.model.unlock_code):
            self.state.entered_code += chr(key)
            self.state.event = Events.LOCK_TYPE

    def undo_enter_code(self, entered_code):
        if entered_code:
            self.state.entered_code = self.state.entered_code[:-1]
            self.state.event = Events.LOCK_TYPE

    def handle_input(self):
        focus_window = self.get_focus_window()
        focus = self.state.focus
        screen = self.state.screen
        entered_code = self.state.entered_code

        key = self.get_input(focus_window)
        if key in [10, 13]:
                if screen == Screens.SIGNIN:
                    self.continue_signin()
                if screen == Screens.BOOT and focus == Focus.LOCK:
                    if len(entered_code) == len(self.model.unlock_code):
                        self.unlock_terminal(entered_code)
        elif key in range(ord('0'), ord('9') + 1):
            if screen == Screens.BOOT and focus == Focus.LOCK:
                self.enter_code(entered_code, key)
        elif key in [curses.KEY_BACKSPACE, 127, 8]:
            if screen == Screens.BOOT and focus == Focus.LOCK:
                self.undo_enter_code(entered_code)

    def draw_view(self):
        match self.state.event:
            case Events.SIGNIN:
                self.view.draw_signin(parent_window=self.view.get_window(), image=TokensDE.SIGNIN)
                self.state.event = None
            case Events.CONTINUE:
                self.view.draw_signin(parent_window=self.view.get_window(), image=TokensDE.SIGNIN, undraw=True)
                self.state.event = Events.LOCK_CHECK
            case Events.LOCK_CHECK:
                if self.model.locked:
                    self.state.event = Events.TERM_LOCKED
                elif not self.model.locked:
                    self.state.event = Events.BOOT
                    self.state.focus = Focus.BOOT
                    self.state.screen = Screens.BOOT
            case Events.BOOT:
                self.view.draw_footer(Others.COPYRIGHT)
                self.view.draw_startup_animation(self.view.get_window(), Logo.DEFAULT)
                self.state.event = None
            case Events.TERM_LOCKED:
                self.view.draw_footer(Others.COPYRIGHT)
                self.view.draw_lock(self.model.unlock_code, self.view.get_window())
                self.state.focus = Focus.LOCK
                self.state.event = None
            case Events.LOCK_TYPE:
                self.get_focus_window().type(self.state.entered_code)
                self.state.event = None
            case Events.TERM_LOCK_SUC:
                self.view.draw_messagebox(TokensDE.MSG_SUCCESS.upper(), Colors.SELECTED, self.get_focus_window())
                self.model.unlock()
                self.state.entered_code = ""
                self.state.event = Events.LOCK_CHECK
            case Events.TERM_LOCK_FAIL:
                self.view.draw_messagebox(TokensDE.MSG_FAIL.upper(), Colors.WARNING, self.get_focus_window())
                self.state.entered_code = ""
                self.state.event = Events.LOCK_CHECK




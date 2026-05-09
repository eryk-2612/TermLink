from states import MessageboxState
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

    def get_window(self, fullscreen=False):
        if fullscreen:
            return self.view.get_window()
        else:
            return self.view.get_window(self.state)

    def init_state(self):
        self.state.running = True
        self.state.screen = Screens.SIGNIN
        self.state.event = None
        self.state.focus = None

    def run(self):
        self.init_state()
        while self.state.running:
            self.handle_input()
            self.update_state()
            self.draw_view()

            self.state.msgbox = None
            self.state.event = None

    def handle_input(self):
        window = self.get_window()
        key = self.get_input(window)
        if key in [10, 13]:
            self.enter_pressed()
        elif key in range(ord('0'), ord('9') + 1):
            self.number_pressed(key)
        elif key in [curses.KEY_BACKSPACE, 127, 8]:
            self.backspace_pressed()

    def enter_pressed(self):
        screen = self.state.screen
        focus = self.state.focus
        entered_code = self.state.entered_code
        if screen == Screens.SIGNIN:
            self.continue_boot()
        if screen == Screens.BOOT and focus == Focus.LOCK:
            if len(entered_code) == len(self.model.unlock_code):
                self.unlock_terminal(entered_code)

    def number_pressed(self, key):
        focus = self.state.focus
        entered_code = self.state.entered_code
        if focus == Focus.LOCK:
            self.enter_code(entered_code, key)

    def backspace_pressed(self):
        focus = self.state.focus
        entered_code = self.state.entered_code
        if focus == Focus.LOCK:
            self.undo_enter_code(entered_code)

    def continue_boot(self):
        self.state.screen = Screens.BOOT

    def unlock_terminal(self, entered_code):
        if entered_code == self.model.unlock_code:
            self.state.msgbox = MessageboxState(True, TokensDE.MSG_SUCCESS, Colors.SELECTED)
            self.model.unlock()
            self.state.entered_code = ""
            self.state.focus = None
        else:
            self.state.msgbox = MessageboxState(True, TokensDE.MSG_FAIL, Colors.WARNING)
            self.state.entered_code = ""
        self.state.focus_window = self.view.get_window()

    def enter_code(self, entered_code, key):
        if len(entered_code) < len(self.model.unlock_code):
            self.state.entered_code += chr(key)

    def undo_enter_code(self, entered_code):
        if entered_code:
            self.state.entered_code = self.state.entered_code[:-1]

    def update_state(self):
        screen = self.state.screen
        event = self.state.event
        focus = self.state.focus
        entered_code = self.state.entered_code

        if screen == Screens.BOOT:
            if self.model.locked:
                self.state.focus = Focus.LOCK

    def draw_view(self):
        screen = self.state.screen
        focus = self.state.focus
        event = self.state.event
        msgbox = self.state.msgbox or MessageboxState(False, "", 0)
        match screen:
            case Screens.SIGNIN:
                self.view.draw_signin(parent_window=self.view.get_window(), image=TokensDE.SIGNIN)
            case Screens.BOOT:
                self.view.undraw_signin(parent_window=self.view.get_window(), image=TokensDE.SIGNIN)
                self.view.draw_footer(Others.COPYRIGHT)
                if focus == Focus.LOCK:
                    self.view.draw_lock(self.model.unlock_code, self.view.get_window())
                    self.get_window().type(self.state.entered_code)
                    if msgbox.show:
                        self.view.draw_messagebox(msgbox.message.upper(), msgbox.color, self.get_window(True))
                else:
                    if msgbox.show:
                        self.view.draw_messagebox(msgbox.message.upper(), msgbox.color, self.get_window(True))
                    self.view.draw_startup_animation(self.view.get_window(), Logo.DEFAULT)
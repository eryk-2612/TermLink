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

    def switch_focus(self, focus):
        self.state.focus = focus

    def trigger_event(self, event):
        self.state.event_queue.append(event)

    def init_state(self):
        self.state.running = True
        self.state.screen = Screens.SIGNIN
        self.state.event = None
        self.state.focus = None
        self.state.boot_completed = False

    def run(self):
        self.init_state()
        while self.state.running:
            self.handle_input()
            self.handle_events()
            self.update_state()
            self.draw_view()

    def handle_input(self):
        window = self.get_window()
        key = self.get_input(window)
        if key in [10, 13]:
            self.enter_pressed()
        elif key in range(ord('0'), ord('9') + 1):
            self.number_pressed(key)
        elif key in range(ord('a'), ord('z') + 1) or key in range(ord('A'), ord('Z') + 1):
            self.char_pressed(key)
        elif key in [curses.KEY_BACKSPACE, 127, 8]:
            self.backspace_pressed()
        return key

    def enter_pressed(self):
        screen = self.state.screen
        focus = self.state.focus
        entered_code = self.state.entered_code
        if screen == Screens.SIGNIN:
            self.trigger_event(Events.SIGNIN)
        if screen == Screens.BOOT and focus == Focus.LOCK:
            if len(entered_code) == len(self.model.unlock_code):
                self.trigger_event(Events.ATTEMPT_UNLOCK)
        if focus == Focus.MSG:
            self.trigger_event(Events.SKIP)

    def number_pressed(self, key):
        focus = self.state.focus
        entered_code = self.state.entered_code
        if focus == Focus.LOCK:
            self.enter_code(entered_code, key)

    def char_pressed(self, key):
        focus = self.state.focus
        entered_code = self.state.entered_code
        if focus == Focus.LOCK:
            self.enter_code(entered_code, key)

    def backspace_pressed(self):
        focus = self.state.focus
        entered_code = self.state.entered_code
        if focus == Focus.LOCK:
            self.undo_enter_code(entered_code)

    def escape_pressed(self):
        screen = self.state.screen
        if screen == Screens.SIGNIN or screen == Screens.BOOT:
            self.trigger_event(Events.QUIT)

    def handle_events(self):
        while self.state.event_queue:
            event = self.state.event_queue[0]
            if self.handle_single_event(event):
                self.state.event_queue.pop(0)
            else:
                break

    def handle_single_event(self, event):
        screen = self.state.screen
        focus = self.state.focus

        if event == Events.QUIT:
            self.quit()
            return True
        if event == Events.SIGNIN:
            self.continue_boot()
            return True
        if event == Events.SKIP:
            self.skip_messagebox()
            return True
        if screen == Screens.BOOT:
            if event == Events.TERM_LOCKED:
                    self.prepare_lock(self.model.unlock_code, self.get_window())
                    return True
            if event == Events.ATTEMPT_UNLOCK:
                    self.unlock_terminal(self.state.entered_code)
                    return True
        return False

    def quit(self):
        self.state.running = False

    def check_term_lock(self):
        if self.model.locked:
            self.trigger_event(Events.TERM_LOCKED)
            self.state.term_locked = True

    def continue_boot(self):
        self.state.screen = Screens.BOOT
        self.check_term_lock()

    def unlock_terminal(self, entered_code):
        if entered_code == self.model.unlock_code:
            self.prepare_messagebox(TokensDE.MSG_SUCCESS, Colors.SELECTED, self.get_window(True))
            self.model.unlock()
            self.state.entered_code = ""
            self.state.term_locked = False
        else:
            self.prepare_messagebox(TokensDE.MSG_FAIL, Colors.SELECTED, self.get_window(True))
            self.state.entered_code = ""
            self.state.term_locked = True

    def prepare_lock(self, code, parent):
        self.view.create_lock(code, parent)
        self.switch_focus(Focus.LOCK)

    def skip_messagebox(self):
        if self.state.msgbox:
            self.state.msgbox.skip()

    def prepare_messagebox(self, text, color, parent):
        self.state.msgbox = self.view.create_messagebox(text.upper(), color, parent)
        self.switch_focus(Focus.MSG)

    def enter_code(self, entered_code, key):
        if len(entered_code) < len(self.model.unlock_code):
            self.state.entered_code += chr(key)

    def undo_enter_code(self, entered_code):
        if entered_code:
            self.state.entered_code = self.state.entered_code[:-1]

    def update_state(self):
        screen = self.state.screen
        focus = self.state.focus
        msgbox = self.state.msgbox

        if screen == Screens.BOOT:
            if focus == Focus.MSG and msgbox:
                if not msgbox.visible:
                    self.view.destroy_messagebox(msgbox)
                    self.state.msgbox = None
                    self.switch_focus(None)
                    self.check_term_lock()

    def draw_view(self):
        screen = self.state.screen
        focus = self.state.focus
        msgbox = self.state.msgbox
        term_locked = self.state.term_locked

        match screen:
            case Screens.SIGNIN:
                self.view.draw_signin(self.get_window(True), TokensDE.SIGNIN)
            case Screens.BOOT:
                self.view.undraw_signin(self.get_window(True), TokensDE.SIGNIN)
                self.view.draw_footer(Others.COPYRIGHT)
                if focus == Focus.LOCK:
                    self.view.draw_lock(self.state.entered_code)
                elif focus == Focus.MSG:
                    self.view.draw_messagebox(msgbox)
                elif not term_locked:
                    self.view.draw_startup_animation(self.get_window(True), Logo.DEFAULT)
                    self.state.boot_completed = True
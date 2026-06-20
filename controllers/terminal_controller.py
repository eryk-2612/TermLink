from core import Events, Logo, TokensDE, Focus, Screens, Colors, Others, Popups
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

    def get_window(self, requested_window=None):
        if not requested_window:
            if self.state.focus == Focus.LOCK:
                return self.view.passcode_window
            if self.state.screen == Screens.SIGNIN:
                return self.view.signin_window
            elif self.state.screen == Screens.BOOT:
                return self.view.fullscreen_window
        if requested_window:
            match requested_window:
                case Screens.SIGNIN:
                    return self.view.signin_window
                case Screens.BOOT:
                    return self.view.fullscreen_window
        return self.view.fullscreen_window

    def clear_focus(self):
        self.state.focus = None

    def clear_popup(self):
        self.state.active_popup = None

    def switch_focus(self, focus):
        self.state.focus = focus

    def activate_popup(self, popup):
        if popup and popup != "":
            self.state.active_popup = popup
        else:
            self.state.active_popup = None

    def trigger_event(self, event):
        self.state.event_queue.append(event)

    def init_state(self):
        self.state.running = True
        self.state.screen = Screens.SIGNIN
        self.state.event = None
        self.state.focus = None
        self.state.boot_completed = False
        self.state.loading_progress = 0
        self.state.boot_logo_drawn = False

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
        elif key is not None and key >= 32:
            self.typekey_pressed(key)
        elif key in [curses.KEY_BACKSPACE, 127, 8]:
            self.backspace_pressed()
        return key

    def enter_pressed(self):
        screen = self.state.screen
        popup = self.state.active_popup
        entered_code = self.state.entered_code

        if screen == Screens.SIGNIN:
            self.trigger_event(Events.SIGNIN)
        if screen == Screens.BOOT:
            if popup == Popups.MSG:
                self.view.skip_messagebox()
            if popup == Popups.LOCK:
                if len(entered_code) == len(self.model.unlock_code):
                    self.unlock_terminal()

    def typekey_pressed(self, key):
        focus = self.state.focus
        entered_code = self.state.entered_code
        if focus == Focus.LOCK and key != 32:
            self.enter_code(entered_code, key)

    def backspace_pressed(self):
        focus = self.state.focus
        entered_code = self.state.entered_code
        if focus == Focus.LOCK:
            self.undo_enter_code(entered_code)

    def escape_pressed(self):
        if self.state.screen == Screens.SIGNIN or self.state.screen == Screens.BOOT:
            self.trigger_event(Events.QUIT)

    def handle_events(self):
        while self.state.event_queue:
            event = self.state.event_queue[0]
            if self.handle_single_event(event):
                self.state.event_queue.pop(0)
            else:
                break

    def handle_single_event(self, event):
        if event == Events.QUIT:
            self.quit()
            return True
        if event == Events.SIGNIN:
            self.boot()
            return True
        return False

    def quit(self):
        self.state.running = False

    def boot(self):
        self.state.screen = Screens.BOOT

    def unlock_terminal(self):
        if self.state.entered_code == self.model.unlock_code:
            self.model.unlock()
            self.prepare_messagebox(TokensDE.MSG_SUCCESS, Colors.SELECTED, self.get_window(Screens.FULLSCREEN))
            self.activate_popup(Popups.MSG)
        else:
            self.prepare_messagebox(TokensDE.MSG_FAIL, Colors.SELECTED, self.get_window(Screens.FULLSCREEN))
            self.activate_popup(Popups.MSG)
        self.state.entered_code = ""

    def prepare_lock(self, code, parent):
        self.view.create_lock(code, parent)

    def skip_messagebox(self):
        if self.view.messagebox_finished:
            self.view.skip_messagebox()

    def prepare_messagebox(self, text, color, parent):
        self.view.create_messagebox(text.upper(), color, parent)

    def enter_code(self, entered_code, key):
        if self.state.screen == Screens.BOOT:
            if len(entered_code) < len(self.model.unlock_code):
                self.state.entered_code += chr(key)

    def undo_enter_code(self, entered_code):
        if entered_code:
            self.state.entered_code = self.state.entered_code[:-1]

    def update_state(self):
        screen = self.state.screen
        popup = self.state.active_popup
        focus = self.state.focus

        if self.view.messagebox_finished:
            if self.state.active_popup == Popups.MSG:
                self.view.destroy_messagebox()
                self.clear_popup()

        if screen == Screens.BOOT:
            if self.model.locked:
                if popup != Popups.MSG:
                    self.activate_popup(Popups.LOCK)
                    self.switch_focus(Focus.LOCK)
            elif not self.model.locked:
                if popup == Popups.LOCK:
                    self.clear_popup()
                if focus == Focus.LOCK:
                    self.switch_focus(None)

        if self.state.loading_progress >= 100 and self.state.boot_logo_drawn:
            self.state.boot_completed = True

    def draw_view(self):
        screen = self.state.screen
        popup = self.state.active_popup
        entered_code = self.state.entered_code

        match screen:
            case Screens.SIGNIN:
                self.view.draw_signin(TokensDE.SIGNIN)
            case Screens.BOOT:
                if self.get_window(Screens.SIGNIN):
                    self.view.undraw_signin(TokensDE.SIGNIN)
                self.view.draw_footer(TokensDE.COPYRIGHT)
                if popup:
                    if popup == Popups.MSG:
                        self.view.draw_messagebox()
                    elif popup == Popups.LOCK:
                        self.view.create_lock(self.model.unlock_code, self.get_window(Screens.FULLSCREEN))
                        self.view.draw_lock(entered_code)
                elif not self.model.locked:
                    self.view.draw_startup_logo(self.get_window(), Logo.DEFAULT)
                    self.state.boot_logo_drawn = True
                    self.view.draw_startup_progressbar(self.get_window(), Logo.DEFAULT, self.state.loading_progress)
                    if self.state.loading_progress >= 100:
                        self.view.clean_up_startup_animation(self.get_window())
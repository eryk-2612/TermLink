from core import Events, Tokens, Focus, Screens, Colors, Popups
from views.render_models import TerminalFrame
from states.state import PopupState
import curses
import time

class TerminalController:
    def __init__(self, stdscr, model, view, state):
        self.model = model
        self._stdscr = stdscr
        self.view = view
        self.state = state
        self._next_start_screen = None

    def input_target(self):
        if self.state.focus == Focus.LOCK:
            return "lock"
        if self.state.screen == Screens.SIGNIN:
            return "signin"
        if self.state.screen == Screens.BOOT:
            return "boot"
        return "fullscreen"

    def clear_focus(self):
        self.state.focus = None

    def clear_popup(self):
        self.state.dismiss_popup()

    def switch_focus(self, focus):
        self.state.focus = focus

    def activate_popup(self, popup):
        if popup and popup != "":
            self.state.show_popup(PopupState(kind=popup))
        else:
            self.state.dismiss_popup()

    def trigger_event(self, event):
        self.state.event_queue.append(event)

    def init_state(self):
        self.state.running = True
        self.state.screen = Screens.BOOT if self.model.skip_signin else Screens.SIGNIN
        self.state.focus = None
        self.state.popup = None
        self.state.entered_code = ""
        self.state.event_queue.clear()
        self.state.boot_completed = False
        self.state.loading_progress = 0
        self.state.boot_logo_drawn = False

    def run(self):
        while True:
            self.init_state()
            if self._next_start_screen is not None:
                self.state.screen = self._next_start_screen
                self._next_start_screen = None
            while self.state.running:
                self.handle_input()
                self.handle_events()
                if not self.state.running:
                    break
                self.update_state()
                if not self.state.running:
                    break
                self.draw_view()
            if self._next_start_screen is None:
                return
            self._stdscr.erase()
            self._stdscr.refresh()

    def handle_input(self):
        key = self.view.read_key(self.input_target())

        if key in [10, 13]:
            self.enter_pressed()
        elif key in [curses.KEY_BACKSPACE, 127, 8]:
            self.backspace_pressed()
        elif key is not None and key >= 32:
            self.typekey_pressed(key)
        return key

    def enter_pressed(self):
        screen = self.state.screen
        popup = self.state.popup.kind if self.state.popup else None
        entered_code = self.state.entered_code

        if screen == Screens.SIGNIN:
            self.trigger_event(Events.SIGNIN)
        if screen == Screens.BOOT:
            if popup == Popups.MSG:
                self.skip_messagebox()
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
        # Subclasses extend handle_single_event so the queue has one dispatch loop.
        while self.state.event_queue and self.state.running:
            event = self.state.event_queue[0]
            if self.handle_single_event(event):
                self.state.event_queue.pop(0)
            else:
                break

    def handle_single_event(self, event):
        if event == Events.LEAVE:
            self._next_start_screen = None
            self.quit()
            return True
        if event == Events.SIGN_OUT:
            self._next_start_screen = Screens.SIGNIN
            self.quit()
            return True
        if event == Events.QUIT:
            should_restart = (
                self.state.screen != Screens.SIGNIN
                and not self.model.skip_signin
            )
            self._next_start_screen = Screens.SIGNIN if should_restart else None
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
            self.prepare_messagebox(Tokens.MSG_SUCCESS, Colors.SELECTED, Screens.BOOT)
        else:
            self.prepare_messagebox(Tokens.MSG_FAIL, Colors.SELECTED, Screens.BOOT)
        self.state.entered_code = ""

    def skip_messagebox(self):
        if self.state.popup:
            self.state.popup.expires_at = time.time()

    def prepare_messagebox(self, text, color, window, delay=1.5):
        # Store popup metadata together to avoid partially updated message state.
        self.state.show_popup(PopupState(
            kind=Popups.MSG,
            text=text.upper(),
            color=color,
            target=window,
            expires_at=time.time() + delay,
        ))

    def destroy_messagebox(self):
        self.view.undraw_messagebox()
        self.clear_popup()

    def enter_code(self, entered_code, key):
        if self.state.screen == Screens.BOOT:
            if len(entered_code) < len(self.model.unlock_code):
                self.state.entered_code += chr(key)

    def undo_enter_code(self, entered_code):
        if entered_code:
            self.state.entered_code = self.state.entered_code[:-1]

    def update_state(self):
        screen = self.state.screen
        popup = self.state.popup.kind if self.state.popup else None
        focus = self.state.focus

        if self.state.popup_expired(time.time()):
            #quit()
            self.destroy_messagebox()

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
        # Project runtime state into a UI-only snapshot before rendering.
        popup = self.state.popup
        popup_kind = popup.kind if popup else ""
        frame = TerminalFrame(
            screen=self.state.screen,
            footer=Tokens.COPYRIGHT,
            entered_code=self.state.entered_code,
            popup_text=popup.text if popup else "",
            popup_color=popup.color if popup else Colors.DEFAULT,
            popup_target=popup.target if popup else Screens.BOOT,
            popup_kind=popup_kind,
            locked=self.model.locked,
            lock_code=self.model.unlock_code,
            logo=tuple(Tokens.LOGO),
            progress=self.state.loading_progress,
            signin=tuple(Tokens.SIGNIN),
        )
        self.view.render(frame)
        if self.state.screen == Screens.BOOT and not self.state.popup and not self.model.locked:
            self.state.boot_logo_drawn = True

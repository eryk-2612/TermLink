import curses

from .terminal_controller import TerminalController
from core import Events, Tokens, Focus, Screens, get_response

class ChatController(TerminalController):
    def __init__(self, stdscr, model, view, state):
        super().__init__(stdscr, model, view, state)

    def init_state(self):
        super().init_state()
        if self.model.previous_response_id:
            self.state.ai_loaded = True
        else:
            self.state.ai_loaded = False
        #self.state.screen = Screens.CHAT # DEBUG ONLY

    def init_ai_chat(self):
        if not self.model.previous_response_id:
            response = get_response(self.model.model, self.model.url, self.model.apikey, "If you understood, only answer with OK", self.model.instructions)

            if response:
                self.model.previous_response_id = response[1]
                self.state.ai_loaded = True
            else:
                self.trigger_event(Events.QUIT)
                self.state.ai_loaded = False

    def get_window(self, requested_window=None):
        win = super().get_window(requested_window)
        if not requested_window:
            if self.state.focus == Focus.LOCK:
                return self.view.passcode_window
            if self.state.screen == Screens.CHAT:
                return self.view.chat_window
        if requested_window:
            match requested_window:
                case Screens.CHAT:
                    return self.view.chat_window
        return win

    def handle_input(self):
        key = super().handle_input()
        if key == curses.KEY_UP:
            self.arrowup_pressed()
        if key == curses.KEY_DOWN:
            self.arrowdown_pressed()
        if key == 27:
            self.escape_pressed()

    def enter_pressed(self):
        super().enter_pressed()
        screen = self.state.screen
        if screen == Screens.CHAT:
            if not self.state.input_text == "":
                self.state.clear_input_text()
                self.trigger_event(Events.SEND_REQUEST)

    def backspace_pressed(self):
        super().backspace_pressed()
        screen = self.state.screen
        if screen == Screens.CHAT:
            self.state.input_text = self.state.input_text[:-1]

    def typekey_pressed(self, key):
        super().typekey_pressed(key)
        screen = self.state.screen

        if screen == Screens.CHAT:
            if not key == curses.KEY_UP and not key == curses.KEY_DOWN:
                self.state.input_text += chr(key)

    def escape_pressed(self):
        super().escape_pressed()
        self.trigger_event(Events.QUIT)

    def arrowdown_pressed(self):
        screen = self.state.screen

        if screen == Screens.CHAT:
            max_scroll = self.view.get_chat_max_scroll()
            self.state.chat_scroll_offset = min(self.state.chat_scroll_offset + 1, max_scroll)

    def arrowup_pressed(self):
        screen = self.state.screen

        if screen == Screens.CHAT:
            if self.state.chat_scroll_offset > 0:
                self.state.chat_scroll_offset -= 1

    def handle_events(self):
        super().handle_events()
        while self.state.event_queue:
            event = self.state.event_queue[0]
            if self._handle_single_event(event):
                self.state.event_queue.pop(0)
            else:
                break

    def _handle_single_event(self, event):
        screen = self.state.screen

        if screen == Screens.CHAT:
            if event == Events.SEND_REQUEST:
                self.send_request()
                return True
        return False

    def send_request(self):
        request = self.state.request
        response = get_response(self.model.model, self.model.url, self.model.apikey, self.model.system_prompt, request, self.model.previous_response_id)

        if response:
            self.state.chat_scroll_offset = 0
            self.state.output_text = (["> " + request]+ response[0].splitlines()+ [""])
            self.model.previous_response_id = response[1]

    def update_state(self):
        super().update_state()

        if not self.state.ai_loaded and self.state.boot_logo_drawn:
            self.init_ai_chat()

        if not self.state.ai_loaded:
            self.state.loading_progress = 50
        else:
            self.state.loading_progress = 100

        if self.state.boot_completed:
            self.state.screen = Screens.CHAT

    def draw_view(self):
        super().draw_view()
        screen = self.state.screen
        output_text = self.state.output_text
        input_text = self.state.input_text

        match screen:
            case Screens.CHAT:
                self.view.draw_footer(Tokens.COPYRIGHT, self.get_window())
                self.view.draw_header(self.model.name.upper())
                self.view.draw_output_window()
                self.view.draw_input_window(input_text)
                self.view.display_text(output_text, self.state.chat_scroll_offset)

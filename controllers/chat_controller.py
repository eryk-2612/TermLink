from .terminal_controller import TerminalController
from core import Events, TokensDE, Focus, Screens, Colors, Others, EntryTypes, Popups, play_audio, stop_audio, get_response

class ChatController(TerminalController):
    def __init__(self, stdscr, model, view, state):
        super().__init__(stdscr, model, view, state)

    def init_state(self):
        super().init_state()
        #self.state.screen = Screens.CHAT # DEBUG ONLY

        if not self.model.previous_response_id:
            self.init_ai_chat()

    def init_ai_chat(self):
        self.model.previous_response_id = get_response(self.model.url, self.model.apikey, "If you understood, only answer with OK", self.model.instructions)[1]

    def get_window(self, requested_window=None):
        win = super().get_window(requested_window)
        if not requested_window:
            if self.state.focus == Focus.LOCK:
                return self.view.passcode_window
            if self.state.screen == Screens.CHAT:
                return self.view.fullscreen_window
        if requested_window:
            match requested_window:
                case Screens.CHAT:
                    return self.view.fullscreen_window
        return win

    def handle_input(self):
        key = super().handle_input()
        if key == 27:
            self.escape_pressed()

    def enter_pressed(self):
        super().enter_pressed()
        screen = self.state.screen
        if screen == Screens.CHAT:
            if self.state.focus == Focus.INPUT:
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
        focus = self.state.focus
        screen = self.state.screen
        if screen == Screens.CHAT:
            if focus == Focus.INPUT:
                self.state.input_text += chr(key)

    def escape_pressed(self):
        super().escape_pressed()
        self.trigger_event(Events.QUIT)

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
        response = get_response(self.model.url, self.model.apikey, self.model.system_prompt, self.state.request, self.model.previous_response_id)
        if response:
            self.state.output_text = response[0].upper() + "\n"
            self.model.previous_response_id = response[1]

    def update_state(self):
        super().update_state()

        if self.state.boot_completed:
            self.state.screen = Screens.CHAT

        if self.state.screen == Screens.CHAT:
            self.state.focus = Focus.INPUT

    def draw_view(self):
        super().draw_view()

        screen = self.state.screen

        match screen:
            case Screens.CHAT:
                self.view.draw_footer(Others.COPYRIGHT)
                self.view.draw_header(self.model.name.upper())
                self.view.draw_output_window(self.state.output_text)
                self.view.draw_input_window(self.state.input_text)

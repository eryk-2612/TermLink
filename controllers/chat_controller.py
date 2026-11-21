import curses

from .terminal_controller import TerminalController
from core import Events, Tokens, Focus, Screens, get_response
from views.render_models import ChatFrame

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

    def input_target(self):
        return "lock" if self.state.focus == Focus.LOCK else "chat"

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
                self.state.submit_input()
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
            self.view.scroll_chat(1)

    def arrowup_pressed(self):
        screen = self.state.screen

        if screen == Screens.CHAT:
            self.view.scroll_chat(-1)

    def handle_single_event(self, event):
        # Handle chat-specific events, then let the base controller handle shared events.
        if self.state.screen == Screens.CHAT and event == Events.SEND_REQUEST:
            self.send_request()
            return True
        return super().handle_single_event(event)

    def send_request(self):
        request = self.state.take_request()
        response = get_response(self.model.model, self.model.url, self.model.apikey, self.model.system_prompt, request, self.model.previous_response_id)

        if response:
            self.view.reset_chat_scroll()
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
        if self.state.screen == Screens.CHAT:
            self.view.render(ChatFrame(
                title=self.model.name,
                footer=Tokens.COPYRIGHT,
                input_text=self.state.input_text,
                output_lines=tuple(self.state.output_text) if isinstance(self.state.output_text, list)
                else tuple(str(self.state.output_text).splitlines()),
            ))

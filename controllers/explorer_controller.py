from .terminal_controller import TerminalController
from states import MessageboxState
from core import Events, Logo, TokensDE, Focus, Screens, Colors, Others
import curses

class ExplorerController(TerminalController):
    def __init__(self, stdscr, model, view, state):
        super().__init__(stdscr, model, view, state)


    def init_state(self):
        super().init_state()

        self.state.screen = Screens.TERMINAL # DEBUG ONLY

    def handle_input(self):
        super().handle_input()

        window = self.get_window()

    def update_state(self):
        super().update_state()

        screen = self.state.screen
        event = self.state.event
        focus = self.state.focus
        entered_code = self.state.entered_code

        if self.state.boot_completed:
            self.state.screen = Screens.TERMINAL

    def draw_view(self):
        super().draw_view()

        screen = self.state.screen
        focus = self.state.focus
        event = self.state.event
        msgbox = self.state.msgbox or MessageboxState(False, "", 0)

        match screen:
             case Screens.TERMINAL:
                self.view.draw_footer(Others.COPYRIGHT)
                self.view.draw_header(self.model.name.upper())
                self.view.draw_categories_window()
                self.view.draw_all_categories(self.model.categories, self.state)



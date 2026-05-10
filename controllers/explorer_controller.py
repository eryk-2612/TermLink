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
        key = super().handle_input()
        if key == curses.KEY_UP:
            self.arrowup_pressed()
        if key == curses.KEY_DOWN:
            self.arrowdown_pressed()

    def enter_pressed(self):
        super().enter_pressed()

        screen = self.state.screen
        focus = self.state.focus
        entered_code = self.state.entered_code

        if screen == Screens.TERMINAL:
            if focus == Focus.ENTRIES:
               pass

    def arrowup_pressed(self):
        screen = self.state.screen
        focus = self.state.focus
        index = self.state.index

        if screen == Screens.TERMINAL:
            if focus == Focus.CATEGORIES:
                if index > 0:
                    self.state.index -= 1
                    if self.state.index < self.state.category_scroll_offset:
                        self.state.category_scroll_offset = self.state.index

    def arrowdown_pressed(self):
        screen = self.state.screen
        focus = self.state.focus
        index = self.state.index
        total_categories = len(self.model.categories)
        visible_categories_count = self.view.get_visible_categories_count()

        if screen == Screens.TERMINAL:
            if focus == Focus.CATEGORIES:
                if index < total_categories - 1:
                    self.state.index += 1
                    if self.state.index >= self.state.category_scroll_offset + visible_categories_count:
                        self.state.category_scroll_offset = self.state.index - visible_categories_count + 1

    def open_category(self, category):
        self.state.open_category = category

    def update_state(self):
        super().update_state()

        screen = self.state.screen
        event = self.state.event
        focus = self.state.focus
        entered_code = self.state.entered_code

        if self.state.boot_completed:
            self.state.screen = Screens.TERMINAL
        if screen == Screens.TERMINAL:
            if focus is None:
                self.state.focus = Focus.CATEGORIES
            if self.state.focus == Focus.CATEGORIES:
                self.state.selected_category = self.state.index
                self.open_category(self.model.categories[self.state.index])

    def draw_view(self):
        super().draw_view()

        screen = self.state.screen
        focus = self.state.focus
        event = self.state.event
        msgbox = self.state.msgbox or MessageboxState(False, "", 0)
        open_category = self.state.open_category

        match screen:
             case Screens.TERMINAL:
                self.view.draw_footer(Others.COPYRIGHT)
                self.view.draw_header(self.model.name.upper())
                self.view.draw_sidebar(self.model.categories, self.state.selected_category, self.state.category_scroll_offset)
                self.view.draw_entry_list(open_category.entries, self.state.selected_entry, self.state.entry_scroll_offset, True if focus == Focus.ENTRIES else False)
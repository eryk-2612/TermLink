from .terminal_controller import TerminalController
from states import MessageboxState
from core import Events, Logo, TokensDE, Focus, Screens, Colors, Others
import curses

class ExplorerController(TerminalController):
    def __init__(self, stdscr, model, view, state):
        super().__init__(stdscr, model, view, state)

    def init_state(self):
        super().init_state()
        #self.state.screen = Screens.TERMINAL # DEBUG ONLY

    def handle_input(self):
        key = super().handle_input()
        if key == curses.KEY_UP:
            self.arrowup_pressed()
        if key == curses.KEY_DOWN:
            self.arrowdown_pressed()
        if key == curses.KEY_LEFT:
            self.arrowleft_pressed()
        if key == curses.KEY_RIGHT:
            self.arrowright_pressed()
        if key == 27:
            self.escape_pressed()

    def enter_pressed(self):
        super().enter_pressed()

        screen = self.state.screen
        focus = self.state.focus

        if screen == Screens.TERMINAL:
            if focus == Focus.CATEGORIES:
                if not self.state.open_category.entries == []:
                    self.trigger_event(Events.OPEN_CATEGORY)
            if focus == Focus.ENTRIES:
               self.trigger_event(Events.OPEN_ENTRY)

    def arrowup_pressed(self):
        screen = self.state.screen
        focus = self.state.focus
        c_index = self.state.c_index
        e_index = self.state.e_index

        if screen == Screens.TERMINAL:
            if focus == Focus.ENTRIES:
                if e_index > 0:
                    self.state.e_index -= 1
                    if self.state.e_index < self.state.entry_scroll_offset:
                        self.state.entry_scroll_offset = self.state.e_index
            if focus == Focus.CATEGORIES:
                if c_index > 0:
                    self.state.c_index -= 1
                    if self.state.c_index < self.state.category_scroll_offset:
                        self.state.category_scroll_offset = self.state.c_index

    def arrowdown_pressed(self):
        screen = self.state.screen
        focus = self.state.focus
        c_index = self.state.c_index
        e_index = self.state.e_index

        if screen == Screens.TERMINAL:
            if focus == Focus.ENTRIES:
                visible_entries_count = self.view.get_visible_entries_count()
                total_entries = len(self.state.open_category.entries)
                if e_index < total_entries - 1:
                    self.state.e_index += 1
                    if self.state.e_index >= self.state.entry_scroll_offset + visible_entries_count:
                        self.state.entry_scroll_offset = self.state.e_index - visible_entries_count + 1
            if focus == Focus.CATEGORIES:
                total_categories = len(self.model.categories)
                visible_categories_count = self.view.get_visible_categories_count()
                if c_index < total_categories - 1:
                    self.state.c_index += 1
                    if self.state.c_index >= self.state.category_scroll_offset + visible_categories_count:
                        self.state.category_scroll_offset = self.state.c_index - visible_categories_count + 1

    def arrowleft_pressed(self):
        screen = self.state.screen
        focus = self.state.focus

        if screen == Screens.TERMINAL:
            if focus == Focus.ENTRIES:
                self.trigger_event(Events.CLOSE_CATEGORY)

    def arrowright_pressed(self):
        screen = self.state.screen
        focus = self.state.focus

        if screen == Screens.TERMINAL:
            if focus == Focus.CATEGORIES:
                if not self.state.open_category.entries == []:
                    self.trigger_event(Events.OPEN_CATEGORY)

    def escape_pressed(self):
        screen = self.state.screen
        focus = self.state.focus

        if screen == Screens.TERMINAL:
            if focus == Focus.ENTRIES:
                self.trigger_event(Events.CLOSE_CATEGORY)

    def handle_event(self):
        super().handle_event()

        screen = self.state.screen
        event = self.state.event

        if screen == Screens.TERMINAL:
            if event == Events.OPEN_CATEGORY:
                self.open_category(self.model.categories[self.state.c_index])
            if event == Events.CLOSE_CATEGORY:
                self.close_category()
            if event == Events.OPEN_ENTRY:
                self.open_entry(self.state.open_category.entries[self.state.e_index])
            if event == Events.CLOSE_ENTRY:
                self.close_entry()

    def preview_category(self, category):
        self.state.open_category = category

    def open_category(self, category):
        self.state.open_category = category
        self.state.e_index = 0
        self.switch_focus(Focus.ENTRIES)

    def close_category(self):
        self.state.open_category = None
        self.state.e_index = 0
        self.state.entry_scroll_offset = 0
        self.switch_focus(Focus.CATEGORIES)

    def open_entry(self, entry):
        #self.set_focus(Focus.CONTENT)
        self.state.open_entry = entry

    def close_entry(self):
        self.state.open_entry = None
        self.state.content_scroll_offset = 0
        self.state.switch_selected = 0
        self.switch_focus(Focus.ENTRIES)

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
                self.switch_focus(Focus.CATEGORIES)
            if self.state.focus == Focus.ENTRIES:
                self.state.selected_entry = self.state.e_index
            if self.state.focus == Focus.CATEGORIES:
                self.state.selected_category = self.state.c_index
                self.preview_category(self.model.categories[self.state.c_index])

    def draw_view(self):
        super().draw_view()

        screen = self.state.screen
        focus = self.state.focus
        msgbox = self.state.msgbox or MessageboxState(False, "", 0)
        open_category = self.state.open_category

        match screen:
             case Screens.TERMINAL:
                self.view.draw_footer(Others.COPYRIGHT)
                self.view.draw_header(self.model.name.upper())
                self.view.draw_sidebar(self.model.categories, self.state.selected_category, self.state.category_scroll_offset, True if focus == Focus.CATEGORIES else False)
                self.view.draw_entry_list(open_category, self.state.selected_entry, self.state.entry_scroll_offset, True if focus == Focus.ENTRIES else False)
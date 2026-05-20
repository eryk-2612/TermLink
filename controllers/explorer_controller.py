from .terminal_controller import TerminalController
from core import Events, Logo, TokensDE, Focus, Screens, Colors, Others, EntryTypes
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
        if key == curses.KEY_LEFT:
            self.arrowleft_pressed()
        if key == curses.KEY_RIGHT:
            self.arrowright_pressed()
        if key == 27:
            self.escape_pressed()

    def enter_pressed(self):
        super().enter_pressed()

        screen = self.state.screen
        open_entry = self.state.open_entry
        focus = self.state.focus
        entered_code = self.state.entered_code

        if screen == Screens.TERMINAL:
            if focus == Focus.CATEGORIES:
                if not self.state.open_category.entries == []:
                    self.trigger_event(Events.OPEN_CATEGORY)
            elif focus == Focus.ENTRIES:
               self.trigger_event(Events.OPEN_ENTRY)
            elif focus == Focus.SWITCH:
                open_entry.current_state = self.state.switch_selected
            elif focus == Focus.LOCK:
                if len(entered_code) == len(open_entry.unlock_code):
                    self.trigger_event(Events.ATTEMPT_UNLOCK)

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
            elif focus == Focus.CATEGORIES:
                if c_index > 0:
                    self.state.c_index -= 1
                    if self.state.c_index < self.state.category_scroll_offset:
                        self.state.category_scroll_offset = self.state.c_index
            elif focus == Focus.CONTENT:
                if self.state.content_scroll_offset > 0:
                    self.state.content_scroll_offset -= 1

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
            elif focus == Focus.CATEGORIES:
                total_categories = len(self.model.categories)
                visible_categories_count = self.view.get_visible_categories_count()
                if c_index < total_categories - 1:
                    self.state.c_index += 1
                    if self.state.c_index >= self.state.category_scroll_offset + visible_categories_count:
                        self.state.category_scroll_offset = self.state.c_index - visible_categories_count + 1
            elif focus == Focus.CONTENT:
                max_scroll = self.view.get_content_max_scroll()
                self.state.content_scroll_offset = min(self.state.content_scroll_offset + 1, max_scroll)

    def arrowleft_pressed(self):
        screen = self.state.screen
        focus = self.state.focus

        if screen == Screens.TERMINAL:
            if focus == Focus.ENTRIES:
                self.trigger_event(Events.CLOSE_CATEGORY)
            elif focus == Focus.SWITCH:
                self.state.switch_selected = 0

    def arrowright_pressed(self):
        screen = self.state.screen
        focus = self.state.focus

        if screen == Screens.TERMINAL:
            if focus == Focus.CATEGORIES:
                if not self.state.open_category.entries == []:
                    self.trigger_event(Events.OPEN_CATEGORY)
            elif focus == Focus.SWITCH:
                self.state.switch_selected = 1

    def escape_pressed(self):
        super().escape_pressed()

        screen = self.state.screen
        focus = self.state.focus

        if screen == Screens.TERMINAL:
            if focus == Focus.ENTRIES:
                self.trigger_event(Events.CLOSE_CATEGORY)
            elif focus == Focus.CONTENT or focus == Focus.SWITCH:
                self.trigger_event(Events.CLOSE_ENTRY)
            elif focus == Focus.LOCK:
                self.trigger_event(Events.CLOSE_ENTRY)

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
        focus = self.state.focus

        if screen == Screens.TERMINAL:
            if event == Events.OPEN_CATEGORY:
                self.open_category(self.model.categories[self.state.c_index])
                return True
            elif event == Events.CLOSE_CATEGORY:
                self.close_category()
                return True
            elif event == Events.OPEN_ENTRY:
                self.open_entry(self.state.open_category.entries[self.state.e_index])
                return True
            elif event == Events.CLOSE_ENTRY:
                self.close_entry()
                return True
            elif event == Events.CONTENT_LOCKED:
                self.prepare_lock(self.state.open_entry.unlock_code, self.get_window())
                return True
            elif event == Events.ATTEMPT_UNLOCK:
                self.unlock_entry(self.state.open_entry, self.state.entered_code)
                return True
        return False

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
        self.switch_focus(Focus.CONTENT)
        self.state.open_entry = entry
        self.check_entry_lock(entry)
        if entry.type == EntryTypes.QUIT:
            self.trigger_event(Events.QUIT)

    def close_entry(self):
        self.state.open_entry = None
        self.state.content_scroll_offset = 0
        self.state.switch_selected = 0
        self.state.entered_code = ""
        self.state.content_locked = False
        if self.state.focus == Focus.LOCK:
            self.view.destroy_lock()
        self.switch_focus(Focus.ENTRIES)

    def check_entry_lock(self, entry):
        if entry.locked:
            self.state.content_locked = True
            self.trigger_event(Events.CONTENT_LOCKED)

    def unlock_entry(self, entry, entered_code):
        self.switch_focus(Focus.CONTENT)
        if entered_code == entry.unlock_code:
            self.prepare_messagebox(TokensDE.MSG_SUCCESS, Colors.SELECTED, self.get_window())
            entry.unlock()
            self.state.entered_code = ""
            self.state.content_locked = False
        else:
            self.prepare_messagebox(TokensDE.MSG_FAIL, Colors.SELECTED, self.get_window())
            self.state.entered_code = ""
            self.state.content_locked = True

    def update_state(self):
        super().update_state()

        screen = self.state.screen
        open_entry = self.state.open_entry
        focus = self.state.focus
        msgbox = self.state.msgbox
        entry = self.state.open_entry

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
            if self.state.focus == Focus.CONTENT and open_entry.type == EntryTypes.SWITCH:
                self.switch_focus(Focus.SWITCH)
            if focus == Focus.MSG and msgbox:
                if not msgbox.visible:
                    msgbox.destroy()
                    self.state.msgbox = None
                    self.switch_focus(Focus.CONTENT)
                    self.check_entry_lock(entry)

    def draw_view(self):
        super().draw_view()

        screen = self.state.screen
        focus = self.state.focus
        open_category = self.state.open_category
        open_entry = self.state.open_entry
        msgbox = self.state.msgbox

        match screen:
             case Screens.TERMINAL:
                self.view.draw_footer(Others.COPYRIGHT)
                self.view.draw_header(self.model.name.upper())
                self.view.draw_sidebar(self.model.categories, self.state.selected_category, self.state.category_scroll_offset, True if focus == Focus.CATEGORIES else False)
                self.view.draw_entry_list(open_category, self.state.selected_entry, self.state.entry_scroll_offset, True if focus == Focus.ENTRIES else False)
                self.view.draw_content_window()
                if open_entry is None:
                    self.view.clear_content()
                elif (focus == Focus.CONTENT or focus == Focus.SWITCH) and not self.state.content_locked:
                    entry_type = open_entry.type
                    if entry_type == EntryTypes.TEXT:
                        self.view.display_text(open_entry.lines, self.state.content_scroll_offset, True if focus == Focus.CONTENT else False)
                    if entry_type == EntryTypes.SWITCH:
                        self.view.display_switch(open_entry.state_labels, open_entry.action_verbs, self.state.switch_selected, open_entry.current_state)
                elif focus == Focus.LOCK:
                    self.view.draw_lock(self.state.entered_code)
                elif focus == Focus.MSG:
                    self.view.draw_messagebox(msgbox)

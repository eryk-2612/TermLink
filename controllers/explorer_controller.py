from .terminal_controller import TerminalController
from core import Events, Tokens, Focus, Screens, Colors, Others, EntryTypes, Popups, play_audio, stop_audio
import curses
import time

class ExplorerController(TerminalController):
    def __init__(self, stdscr, model, view, state):
        super().__init__(stdscr, model, view, state)

    def init_state(self):
        super().init_state()
        self.state.loading_progress = 100
        #self.state.screen = Screens.EXPLORER # DEBUG ONLY

    def get_window(self, requested_window=None):
        win = super().get_window(requested_window)
        if not requested_window:
            if self.state.focus == Focus.LOCK:
                return self.view.passcode_window
            if self.state.focus == Focus.CONTENT:
                return self.view.content_window
            if self.state.screen == Screens.EXPLORER:
                return self.view.explorer_window
        if requested_window:
            match requested_window:
                case Screens.EXPLORER:
                    return self.view.fullscreen_window
                case Focus.CONTENT:
                    return self.view.content_window
        return win

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
        elif key == 32:
            self.spacebar_pressed()
        if key == 27:
            self.escape_pressed()

    def enter_pressed(self):
        super().enter_pressed()

        screen = self.state.screen
        open_entry = self.state.open_entry
        focus = self.state.focus
        popup = self.state.active_popup
        entered_code = self.state.entered_code

        if screen == Screens.EXPLORER:
            if focus == Focus.CATEGORIES:
                if self.state.open_category and not self.state.open_category.entries == []:
                    self.trigger_event(Events.OPEN_CATEGORY)
            elif focus == Focus.ENTRIES:
               self.trigger_event(Events.OPEN_ENTRY)
            elif focus == Focus.CONTENT:
                if open_entry.type == EntryTypes.SWITCH:
                    open_entry.current_state = self.state.switch_selected
                if open_entry.type == EntryTypes.BUTTON:
                    if not open_entry.current_state:
                        open_entry.current_state = True
                        self.prepare_messagebox(open_entry.message, Colors.SELECTED, self.get_window(Focus.CONTENT))
                        self.activate_popup(Popups.MSG)
            elif popup == Popups.LOCK:
                if len(entered_code) == len(open_entry.unlock_code):
                    self.unlock_entry()
            if popup == Popups.MSG:
                self.view.skip_messagebox()

    def spacebar_pressed(self):
        screen = self.state.screen
        focus = self.state.focus
        open_entry = self.state.open_entry

        if screen == Screens.EXPLORER:
            if focus == Focus.CONTENT:
                if open_entry.type == EntryTypes.AUDIO:
                    if not open_entry.is_playing:
                        self.play_audio(open_entry)
                    else:
                        self.stop_audio()

    def arrowup_pressed(self):
        screen = self.state.screen
        focus = self.state.focus
        category_index = self.state.category_index
        entry_index = self.state.entry_index
        open_entry = self.state.open_entry

        if screen == Screens.EXPLORER:
            if focus == Focus.CATEGORIES:
                if category_index > 0:
                    self.state.category_index -= 1
                    if self.state.category_index < self.state.category_scroll_offset:
                        self.state.category_scroll_offset = self.state.category_index
            elif focus == Focus.ENTRIES:
                if entry_index > 0:
                    self.state.entry_index -= 1
                    if self.state.entry_index < self.state.entry_scroll_offset:
                        self.state.entry_scroll_offset = self.state.entry_index
            elif focus == Focus.CONTENT:
                if self.state.content_scroll_offset == 0:
                    self.trigger_event(Events.CLOSE_ENTRY)
                if open_entry.type == EntryTypes.TEXT:
                    if self.state.content_scroll_offset > 0:
                        self.state.content_scroll_offset -= 1
            elif focus == Focus.LOCK:
                self.trigger_event(Events.CLOSE_ENTRY)

    def arrowdown_pressed(self):
        screen = self.state.screen
        focus = self.state.focus
        category_index = self.state.category_index
        entry_index = self.state.entry_index

        if screen == Screens.EXPLORER:
            if focus == Focus.CATEGORIES:
                total_categories = len(self.model.categories)
                visible_categories_count = self.view.get_visible_categories_count()
                if category_index < total_categories - 1:
                    self.state.category_index += 1
                    if self.state.category_index >= self.state.category_scroll_offset + visible_categories_count:
                        self.state.category_scroll_offset = self.state.category_index - visible_categories_count + 1
            elif focus == Focus.ENTRIES:
                visible_entries_count = self.view.get_visible_entries_count()
                total_entries = len(self.state.open_category.entries)
                if entry_index < total_entries - 1:
                    self.state.entry_index += 1
                    if self.state.entry_index >= self.state.entry_scroll_offset + visible_entries_count:
                        self.state.entry_scroll_offset = self.state.entry_index - visible_entries_count + 1
            elif focus == Focus.CONTENT:
                max_scroll = self.view.get_content_max_scroll()
                self.state.content_scroll_offset = min(self.state.content_scroll_offset + 1, max_scroll)

    def arrowleft_pressed(self):
        screen = self.state.screen
        focus = self.state.focus
        open_entry = self.state.open_entry

        if screen == Screens.EXPLORER:
            if focus == Focus.ENTRIES:
                self.trigger_event(Events.CLOSE_CATEGORY)
            elif focus == Focus.CONTENT:
                if open_entry.type == EntryTypes.SWITCH:
                    self.state.switch_selected = 0

    def arrowright_pressed(self):
        screen = self.state.screen
        focus = self.state.focus
        open_entry = self.state.open_entry

        if screen == Screens.EXPLORER:
            if focus == Focus.CATEGORIES:
                if self.state.open_category and not self.state.open_category.entries == []:
                    self.trigger_event(Events.OPEN_CATEGORY)
            elif focus == Focus.CONTENT:
                if open_entry.type == EntryTypes.SWITCH:
                    self.state.switch_selected = 1

    def escape_pressed(self):
        super().escape_pressed()

        screen = self.state.screen
        focus = self.state.focus

        if screen == Screens.EXPLORER:
            if focus == Focus.ENTRIES:
                self.trigger_event(Events.CLOSE_CATEGORY)
            elif focus == Focus.CONTENT or focus == Focus.LOCK:
                self.trigger_event(Events.CLOSE_ENTRY)

    def enter_code(self, entered_code, key):
        super().enter_code(entered_code, key)
        if self.state.open_entry:
            if len(entered_code) < len(self.state.open_entry.unlock_code):
                self.state.entered_code += chr(key)

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

        if screen == Screens.EXPLORER:
            if event == Events.OPEN_CATEGORY:
                self.open_category(self.model.categories[self.state.category_index])
                return True
            elif event == Events.CLOSE_CATEGORY:
                self.close_category()
                return True
            elif event == Events.OPEN_ENTRY:
                self.open_entry(self.state.open_category.entries[self.state.entry_index])
                return True
            elif event == Events.CLOSE_ENTRY:
                self.close_entry()
                return True
        return False

    def preview_category(self, category):
        self.state.open_category = category

    def open_category(self, category):
        self.state.open_category = category
        self.state.entry_index = 0
        self.switch_focus(Focus.ENTRIES)

    def close_category(self):
        self.state.open_category = None
        self.state.entry_index = 0
        self.state.entry_scroll_offset = 0
        self.switch_focus(Focus.CATEGORIES)

    def open_entry(self, entry):
        self.switch_focus(Focus.CONTENT)
        self.state.open_entry = entry

        if entry.locked:
            self.activate_popup(Popups.LOCK)
            self.switch_focus(Focus.LOCK)
        else:
            if entry.type == EntryTypes.SWITCH:
                self.state.switch_selected = entry.current_state
            if entry.type == EntryTypes.QUIT:
                self.trigger_event(Events.QUIT)

    def play_audio(self, entry):
        path = Others.DATA_PATH + entry.audio
        success = play_audio(path)
        entry.is_playing = success
        if success:
            entry.audio_start_time = time.time()

    def stop_audio(self):
        stop_audio()
        self.state.open_entry.is_playing = False
        self.state.open_entry.audio_start_time = 0

    def close_entry(self):
        if self.state.open_entry.type == EntryTypes.AUDIO:
            self.stop_audio()

        self.state.content_scroll_offset = 0
        self.state.switch_selected = 0
        self.state.entered_code = ""
        self.clear_popup()
        self.switch_focus(Focus.ENTRIES)
        self.state.open_entry = None

    def unlock_entry(self):
        if self.state.entered_code == self.state.open_entry.unlock_code:
            self.state.open_entry.unlock()
            self.prepare_messagebox(Tokens.MSG_SUCCESS, Colors.SELECTED, self.get_window(Focus.CONTENT))
            self.activate_popup(Popups.MSG)
        else:
            self.prepare_messagebox(Tokens.MSG_FAIL, Colors.SELECTED, self.get_window(Focus.CONTENT))
            self.activate_popup(Popups.MSG)
        self.state.entered_code = ""

    def update_state(self):
        super().update_state()

        screen = self.state.screen
        focus = self.state.focus
        entry = self.state.open_entry

        if self.state.boot_completed:
            self.state.screen = Screens.EXPLORER
        if screen == Screens.EXPLORER:
            if focus is None:
                self.switch_focus(Focus.CATEGORIES)
            elif self.state.focus == Focus.ENTRIES:
                self.state.selected_entry = self.state.entry_index
            elif self.state.focus == Focus.CATEGORIES:
                self.state.selected_category = self.state.category_index
                self.preview_category(self.model.categories[self.state.category_index])
            elif self.state.focus == Focus.LOCK:
                if not self.state.open_entry.locked and self.view.messagebox_finished:
                    self.switch_focus(Focus.CONTENT)
                    if entry.type == EntryTypes.QUIT:
                        self.trigger_event(Events.QUIT)
                else:
                    if self.view.messagebox_finished:
                        self.open_entry(self.state.open_category.entries[self.state.entry_index])

    def draw_view(self):
        super().draw_view()

        screen = self.state.screen
        focus = self.state.focus
        open_category = self.state.open_category
        open_entry = self.state.open_entry
        active_popup = self.state.active_popup
        entered_code = self.state.entered_code

        match screen:
             case Screens.EXPLORER:
                self.view.draw_footer(Tokens.COPYRIGHT, self.get_window())
                self.view.draw_header(self.model.name.upper())
                self.view.draw_sidebar(self.model.categories, self.state.selected_category, self.state.category_scroll_offset, True if focus == Focus.CATEGORIES else False)
                self.view.draw_entry_list(open_category, self.state.selected_entry, self.state.entry_scroll_offset, True if focus == Focus.ENTRIES else False)
                self.view.draw_content_window()
                if open_entry is None:
                    self.view.clear_content()
                    if active_popup:
                        self.view.destroy_messagebox()
                        self.view.destroy_lock()
                else:
                    if active_popup:
                        if active_popup == Popups.MSG:
                            self.view.draw_messagebox()
                        elif active_popup == Popups.LOCK:
                            self.view.create_lock(open_entry.unlock_code, self.get_window(Focus.CONTENT))
                            self.view.draw_lock(entered_code)
                    elif not open_entry.locked:
                        entry_type = open_entry.type
                        if entry_type == EntryTypes.TEXT:
                            self.view.display_text(open_entry.lines, self.state.content_scroll_offset, True if focus == Focus.CONTENT else False)
                        elif entry_type == EntryTypes.SWITCH:
                            self.view.display_switch(open_entry.state_labels, open_entry.action_verbs, self.state.switch_selected, open_entry.current_state)
                        elif entry_type == EntryTypes.BUTTON:
                            self.view.display_button(open_entry.state_labels, open_entry.action_verbs, open_entry.current_state)
                        elif entry_type == EntryTypes.AUDIO:
                            if open_entry.is_playing:
                                elapsed_time = min((time.time() - open_entry.audio_start_time), open_entry.audio_length)
                            else:
                                elapsed_time = 0
                            self.view.display_audioplayer(open_entry.is_playing, open_entry.audio_length, elapsed_time)
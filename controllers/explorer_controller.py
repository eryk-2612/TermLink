from .terminal_controller import TerminalController
from core import Events, Tokens, Focus, Screens, Colors, Others, EntryTypes, Popups, play_audio, stop_audio, FloppyManager, JsonLoader
from views.render_models import ExplorerFrame, EntryFrame
import curses
import time

class ExplorerController(TerminalController):
    def __init__(self, stdscr, model, view, state, disk_loaded=False):
        super().__init__(stdscr, model, view, state)
        self.floppy = FloppyManager()
        self._initial_disk_notification_pending = disk_loaded
        self._silent_initial_disk_load = False

    def init_state(self):
        super().init_state()
        self.state.loading_progress = 100
        self.state.floppy_init = False
        #self.state.screen = Screens.EXPLORER # DEBUG ONLY

    def input_target(self):
        if self.state.focus == Focus.LOCK:
            return "lock"
        if self.state.focus == Focus.CONTENT:
            return "content"
        return "explorer"

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
        popup = self.state.popup.kind if self.state.popup else None
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
                        self.prepare_messagebox(open_entry.message, Colors.SELECTED, Focus.CONTENT)
            elif popup == Popups.LOCK:
                if len(entered_code) == len(open_entry.unlock_code):
                    self.unlock_entry()
            if popup == Popups.MSG:
                self.skip_messagebox()

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
                    self.view.keep_selection_visible(
                        "categories", self.state.category_index, len(self.model.categories)
                    )
            elif focus == Focus.ENTRIES:
                if entry_index > 0:
                    self.state.entry_index -= 1
                    self.view.keep_selection_visible(
                        "entries", self.state.entry_index,
                        len(self.state.open_category.entries)
                    )
            elif focus == Focus.CONTENT:
                if not self.view.scroll_content(-1):
                    self.trigger_event(Events.CLOSE_ENTRY)
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
                if category_index < total_categories - 1:
                    self.state.category_index += 1
                    self.view.keep_selection_visible(
                        "categories", self.state.category_index, total_categories
                    )
            elif focus == Focus.ENTRIES:
                total_entries = len(self.state.open_category.entries)
                if entry_index < total_entries - 1:
                    self.state.entry_index += 1
                    self.view.keep_selection_visible(
                        "entries", self.state.entry_index, total_entries
                    )
            elif focus == Focus.CONTENT:
                self.view.scroll_content(1)

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

    def handle_single_event(self, event):
        # Keep navigation transitions here while sharing the base event queue loop.
        if self.state.screen == Screens.EXPLORER:
            if event == Events.OPEN_CATEGORY:
                self.open_category(self.model.categories[self.state.category_index])
                return True
            if event == Events.CLOSE_CATEGORY:
                self.close_category()
                return True
            if event == Events.OPEN_ENTRY:
                self.open_entry(self.state.open_category.entries[self.state.entry_index])
                return True
            if event == Events.CLOSE_ENTRY:
                self.close_entry()
                return True
        return super().handle_single_event(event)

    def quit(self):
        self.unload_categories_from_floppy()
        self.state.floppy_data_loaded = False
        self.state.floppy_init = False
        self.destroy_header_notification()
        self.state.running = False

    def preview_category(self, category):
        self.state.open_category = category

    def open_category(self, category):
        # Opening a category starts its entry list at the first item and viewport row.
        self.state.open_category = category
        self.state.entry_index = 0
        self.view.reset_list_scroll("entries")
        self.switch_focus(Focus.ENTRIES)

    def close_category(self):
        self.state.open_category = None
        self.state.entry_index = 0
        self.view.reset_list_scroll("entries")
        self.switch_focus(Focus.CATEGORIES)

    def open_entry(self, entry):
        # Reset view-owned content scrolling whenever a different entry is opened.
        self.switch_focus(Focus.CONTENT)
        self.view.reset_content_scroll()
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

        self.state.switch_selected = 0
        self.state.entered_code = ""
        self.clear_popup()
        self.switch_focus(Focus.ENTRIES)
        self.state.open_entry = None
        self.state.clear_content = True

    def unlock_entry(self):
        if self.state.entered_code == self.state.open_entry.unlock_code:
            self.state.open_entry.unlock()
            self.prepare_messagebox(Tokens.MSG_SUCCESS, Colors.SELECTED, Focus.CONTENT)
        else:
            self.prepare_messagebox(Tokens.MSG_FAIL, Colors.SELECTED, Focus.CONTENT)
        self.state.entered_code = ""

    def update_state(self):
        super().update_state()

        screen = self.state.screen
        focus = self.state.focus
        entry = self.state.open_entry

        if self.state.boot_completed:
            self.state.screen = Screens.EXPLORER
        if screen == Screens.EXPLORER:
            if self.state.show_notification and self.state.notification_timeout and time.time() > self.state.notification_timeout:
                self.destroy_header_notification()
            self.check_floppy()
            if focus is None:
                self.switch_focus(Focus.CATEGORIES)
            elif self.state.focus == Focus.CATEGORIES:
                if self.model.categories:
                    self.preview_category(self.model.categories[self.state.category_index])
            elif self.state.focus == Focus.LOCK:
                has_message = self.state.popup and self.state.popup.kind == Popups.MSG
                if not self.state.open_entry.locked and not has_message:
                    self.switch_focus(Focus.CONTENT)
                    if entry.type == EntryTypes.QUIT:
                        self.trigger_event(Events.QUIT)
                else:
                    if not has_message:
                        self.open_entry(self.state.open_category.entries[self.state.entry_index])

    def create_header_notification(self, text):
        self.destroy_header_notification()
        self.state.notification = text
        self.state.show_notification = True
        self.state.notification_timeout = time.time() + 3

    def destroy_header_notification(self):
        self.state.notification = ""
        self.state.show_notification = False
        self.state.notification_timeout = None

    def check_floppy(self):
        event = self.floppy.update()

        if self._initial_disk_notification_pending:
            if event == "inserted":
                self._initial_disk_notification_pending = False
                self._silent_initial_disk_load = True
                self.state.floppy_init = True
            elif event in ("unchanged", "removed"):
                self._initial_disk_notification_pending = False

        if event == "inserted":
            if not self.state.floppy_init:
                self.create_header_notification(Tokens.FLOPPY_INSERTED)
                self.state.floppy_init = True

        elif event == "removed":
            if self.state.floppy_drive_found:
                self.state.floppy_drive_found = False
                self.unload_categories_from_floppy()
                self.state.floppy_data_loaded = False
                self.create_header_notification(Tokens.FLOPPY_REMOVED)
            self.state.floppy_init = False
            self._silent_initial_disk_load = False

        elif event == "unchanged":
            if self.state.floppy_init and not self.state.floppy_data_loaded:
                mountpoint = self.floppy.mountpoint

                if mountpoint is None:
                    mountpoint = self.floppy.mount()

                if mountpoint:
                    self.state.floppy_drive_found = True
                    self.load_categories_from_floppy(mountpoint)
                    self.state.floppy_data_loaded = True
                    if self._silent_initial_disk_load:
                        self._silent_initial_disk_load = False
                    else:
                        self.create_header_notification(Tokens.FLOPPY_LOADED)

        return False

    def load_categories_from_floppy(self, mountpoint):
        loader = JsonLoader(mountpoint)
        categories = loader.get_all_categories(mountpoint)
        for c in categories:
            self.model.add_temporary_category(c)

    def unload_categories_from_floppy(self):
        self.model.remove_all_temporary_categories()
        if self.state.category_index >= len(self.model.categories):
            self.state.category_index = len(self.model.categories) - 1 if self.model.categories else 0
            self.view.keep_selection_visible("categories", self.state.category_index, len(self.model.categories))

    def draw_view(self):
        # Convert domain entries to display data so the view never needs model objects.
        super().draw_view()
        if self.state.screen != Screens.EXPLORER:
            return

        category = self.state.open_category
        entry = self.state.open_entry
        entry_frame = None
        if entry:
            entry_frame = EntryFrame(
                kind=entry.type,
                lines=tuple(entry.lines or ()),
                state_labels=tuple(entry.state_labels or ()),
                action_verbs=tuple(entry.action_verbs or ()),
                switch_selected=self.state.switch_selected,
                current_state=entry.current_state,
                is_playing=entry.is_playing,
                audio_length=entry.audio_length,
                elapsed_time=min(time.time() - entry.audio_start_time, entry.audio_length)
                if entry.is_playing else 0,
            )
        popup = self.state.popup
        popup_kind = popup.kind if popup else ""
        self.view.render(ExplorerFrame(
            title=self.model.name,
            footer=Tokens.EXPLORER_HINT,
            categories=tuple(item.title for item in self.model.categories),
            category_index=self.state.category_index,
            entries=tuple(item.title for item in category.entries) if category else (),
            entry_index=self.state.entry_index,
            focus=self.state.focus or "",
            entry=entry_frame,
            notification=self.state.notification if self.state.show_notification else "",
            popup_text=popup.text if popup else "",
            popup_color=popup.color if popup else Colors.DEFAULT,
            popup_kind=popup_kind,
            entered_code=self.state.entered_code,
            locked=bool(entry and entry.locked),
            lock_code=entry.unlock_code if entry else "",
            clear_content=self.state.clear_content,
            category_title=(
                category.title
                if category and self.state.focus != Focus.CATEGORIES
                else ""
            ),
            entry_title=entry.title if entry else "",
        ))
        self.state.clear_content = False

from views.terminal_view import TerminalView
from .window import Window
from .scrollbar import draw_vertical_scrollbar
from core import Colors, Others, Tokens
from .render_models import ExplorerFrame, TerminalFrame

class ExplorerView(TerminalView):
    def __init__(self, stdscr):
        super().__init__(stdscr)
        self._header = None
        self._header_display = None
        self._sidebar = None
        self._entry_list = None
        self._content = None
        self._content_inner = None
        self._content_scrollbar = None
        self._sidebar_scrollbar = None
        self._entries_scrollbar = None
        self._switch_left = None
        self._switch_right = None
        self._button = None
        self._audioplayer = None
        self._categories = []
        self._entries = []
        self._visible_categories_count = 0
        self._visible_entries_count = 0
        self._explorer = None
        self._category_scroll_offset = 0
        self._entry_scroll_offset = 0
        self._content_scroll_offset = 0

    @property
    def sidebar_window(self):
        return self._sidebar

    @property
    def explorer_window(self):
        if not self._explorer:
            self._explorer = Window(self._screen_height, self._screen_width, 0, 0)
        return self._explorer

    @property
    def entry_list_window(self):
        return self._entry_list

    @property
    def content_window(self):
        return self._content

    def read_key(self, target="explorer"):
        if target == "lock":
            return super().read_key(target)
        window = self.content_window if target == "content" else self.explorer_window
        return window.win.getch() if window else None

    def render(self, frame: ExplorerFrame):
        if isinstance(frame, TerminalFrame):
            return super().render(frame)
        self.draw_footer(frame.footer, self.explorer_window)
        if frame.notification:
            self.draw_notification_header(frame.notification)
        else:
            self.draw_header(frame.title)
        self.draw_sidebar(frame.categories, frame.category_index,
                          self._category_scroll_offset, frame.focus == "categories")
        self.draw_entry_list(frame.entries, frame.entry_index,
                             self._entry_scroll_offset, frame.focus == "entries")
        self.draw_content_window()
        if frame.clear_content:
            self.clear_content()
        if frame.popup_kind == "msg":
            self.draw_messagebox(frame.popup_text, frame.popup_color, self.content_window)
            return
        if frame.popup_kind == "lock":
            self.draw_lock(frame.lock_code, self.content_window, frame.entered_code)
            return
        entry = frame.entry
        if not entry or frame.locked:
            return
        if entry.kind == "text":
            self.display_text(entry.lines, self._content_scroll_offset,
                              frame.focus == "content")
        elif entry.kind == "switch":
            self.display_switch(entry.state_labels, entry.action_verbs,
                                entry.switch_selected, entry.current_state)
        elif entry.kind == "button":
            self.display_button(entry.state_labels, entry.action_verbs, entry.current_state)
        elif entry.kind == "audio":
            self.display_audioplayer(entry.is_playing, entry.audio_length, entry.elapsed_time)

    def keep_selection_visible(self, target, index, total):
        # Translate logical selection into viewport offsets without exposing geometry.
        if target == "categories":
            offset_name, visible = "_category_scroll_offset", self._visible_categories_count
        else:
            offset_name, visible = "_entry_scroll_offset", self._visible_entries_count
        visible = max(1, visible)
        offset = getattr(self, offset_name)
        if index < offset:
            offset = index
        elif index >= offset + visible:
            offset = index - visible + 1
        setattr(self, offset_name, min(offset, max(0, total - visible)))

    def reset_list_scroll(self, target):
        if target == "categories":
            self._category_scroll_offset = 0
        else:
            self._entry_scroll_offset = 0

    def scroll_content(self, direction):
        # Return whether movement occurred so the controller can handle boundary keys.
        previous = self._content_scroll_offset
        maximum = self.get_content_max_scroll()
        self._content_scroll_offset = min(max(0, previous + direction), maximum)
        return self._content_scroll_offset != previous

    def reset_content_scroll(self):
        self._content_scroll_offset = 0

    @staticmethod
    def _center_in_content(parent, width, height):
        """Center a child box within the usable area inside the content border."""
        inner_width = max(0, parent.width - 2)
        inner_height = max(0, parent.height - 2)
        x = 1 + (inner_width - width) // 2
        y = 1 + (inner_height - height) // 2
        return y, x

    def get_visible_categories_count(self):
        return self._visible_categories_count

    def get_visible_entries_count(self):
        return self._visible_entries_count

    def get_content_max_scroll(self):
        if not self._content_inner:
            return 0
        return self._content_inner.get_max_scroll_offset()

    def draw_header(self, title="", force=False):
        self._render_header(title, Colors.SELECTED, centered=False, force=force)

    def draw_notification_header(self, notification):
        self._render_header(notification, Colors.DEFAULT, centered=True)

    def _render_header(self, text, color, centered, force=False):
        """Reuse the header window and redraw it whenever its content or style changes."""
        display = (text.upper(), color, centered)
        if self._header is None:
            self._header = Window(1, self._explorer.width, 0, 0, parent_window=self._explorer)
        if display == self._header_display and not force:
            return

        self._header.background = color
        self._header.empty()
        x = (self._header.width - len(display[0])) // 2 if centered else 1
        self._header.write_simple(display[0], y=0, x=x, color=color, bold=True)
        self._header.refresh()
        self._header_display = display

    def draw_sidebar(self, categories, selected_category, category_scroll_offset, in_focus):
        if not self._sidebar:
            height = (self._explorer.height - self._header.height - self._footer.height - Others.SCREEN_PADDING)
            width = self._explorer.width // 4 + Others.SCROLLBAR_PADDING
            self._sidebar = Window(height, width, self._header.start_y + 2, 1, parent_window=self._explorer)
        self.draw_all_categories(categories, selected_category, category_scroll_offset, in_focus)

    def draw_all_categories(self, categories, selected_category, category_scroll_offset, in_focus):
        max_box_height = 8
        min_box_height = 5
        minimum_categories = Others.MINIMUM_CATEGORIES
        maximum_categories = Others.MAXIMUM_CATEGORIES

        available_height = self._sidebar.height - 1
        total_categories = len(categories)
        box_width = self._sidebar.width - Others.SCROLLBAR_PADDING
        length, box_height = self._calculate_category_layout(
            available_height, total_categories, minimum_categories, maximum_categories
        )

        scroll_offset = min(category_scroll_offset, max(0, total_categories - length))
        total_height = length * box_height
        y = max(0, self._sidebar.height - total_height)

        self._sidebar.write_simple(Tokens.FOLDER.upper(), y - 1, 0)
        self._sidebar_scrollbar = self.draw_scrollbar( self._sidebar, self._sidebar_scrollbar, total_height, total_categories, length, scroll_offset, y, self._sidebar.width - 1, in_focus)

        while len(self._categories) < length:
            self._categories.append(None)

        for i in range(length):
            if y + box_height > self._sidebar.height:
                break

            actual_index = scroll_offset + i
            if actual_index >= total_categories:
                title, bgcolor, txtcolor = "", Colors.DEFAULT, Colors.DEFAULT
            else:
                title = categories[actual_index]
                bgcolor = Colors.SELECTED if selected_category == actual_index and in_focus else Colors.DEFAULT
                txtcolor = bgcolor

            self.draw_category(title, y, box_height, box_width, i, bgcolor, txtcolor)
            y += box_height

        self._visible_categories_count = length

    @staticmethod
    def _calculate_category_layout(available_height, total_categories, minimum, maximum):
        """Return the visible category count and category box height."""
        min_box_height = 5
        max_box_height = 8
        max_fit_by_min_height = available_height // min_box_height

        if minimum == -1:
            length = max_fit_by_min_height
            if maximum >= 0:
                length = min(length, maximum)
        elif minimum > 0:
            max_actual = maximum if maximum >= 0 else total_categories
            max_actual = max(max_actual, minimum)
            length = min(max(total_categories, minimum), max_fit_by_min_height, max_actual)
        else:
            max_actual = maximum if maximum >= 0 else total_categories
            length = min(total_categories, max_fit_by_min_height, max_actual)

        length = max(1, length)
        box_height = available_height // length
        box_height = max(min_box_height, min(box_height, max_box_height))

        possible_length = available_height // box_height
        if maximum >= 0:
            possible_length = min(possible_length, maximum)
        length = min(length, possible_length)

        box_height = available_height // length
        box_height = max(min_box_height, min(box_height, max_box_height))
        return length, box_height

    def draw_category(self, title,y, box_height, box_width, wid, bgcolor, txtcolor):
        while len(self._categories) <= wid:
            self._categories.append(None)

        if self._categories[wid] is None:
            win = Window(box_height, box_width, y, 0, 0, wid, self._sidebar)
            self._categories[wid] = win
        else:
            win = self._categories[wid]

        win.background = bgcolor
        win.draw_box()
        win.empty(len(title))
        win.write_animate(title.upper(), 1, 2, 0, txtcolor, True)
        win.refresh()

    def draw_entry_list(self, entries, selected_entry, entry_scroll_offset, in_focus):
        box_height = 3
        if entries:
            if not self._entry_list:
                sidebar_spacing = Others.SCROLLBAR_PADDING
                height = self.calculate_entry_list_height(box_height, entries)
                width = ((self._explorer.width - Others.SCREEN_PADDING) - self._sidebar.width - sidebar_spacing) //  3 * 2
                x = self._sidebar.width + sidebar_spacing
                self._entry_list = Window(height, width, self._header.start_y + 1, x, parent_window=self._explorer)
            self.draw_all_entries(box_height, entries, selected_entry, entry_scroll_offset, in_focus)

    def calculate_entry_list_height(self, box_height, entries, minimum_entries=Others.MINIMUM_ENTRIES, maximum_entries=Others.MAXIMUM_ENTRIES, y_offset=2):
        total_entries = len(entries)
        if maximum_entries > 0:
            possible_length = min(total_entries, maximum_entries)
        else:
            possible_length = total_entries
        visible_entries = max(possible_length, minimum_entries)
        visible_entries = max(visible_entries, 1)
        required_height = visible_entries * box_height + y_offset
        return required_height

    def draw_all_entries(self, box_height, entries, selected_entry, entry_scroll_offset, in_focus):
        y = 2

        box_width = self._entry_list.width - Others.SCROLLBAR_PADDING
        available_height = self._entry_list.height - y
        total_entries = len(entries)
        length = self._calculate_visible_entry_count(
            available_height,
            total_entries,
            Others.MINIMUM_ENTRIES,
            Others.MAXIMUM_ENTRIES,
            box_height,
        )

        total_height = length * box_height
        scroll_offset = min(entry_scroll_offset, max(0, total_entries - length))

        self._entry_list.write_simple(Tokens.FILES.upper(), y - 1, 0)
        self._entries_scrollbar = self.draw_scrollbar(self._entry_list, self._entries_scrollbar, total_height, total_entries,length, scroll_offset, y, self._entry_list.width - 1, in_focus)

        while len(self._entries) < length:
            self._entries.append(None)

        current_y = y
        for i in range(length):
            if current_y + box_height > self._entry_list.height:
                break

            actual_index = scroll_offset + i
            if actual_index >= total_entries:
                title, bgcolor, txtcolor = "", Colors.DEFAULT, Colors.DEFAULT
            else:
                title = entries[actual_index]
                bgcolor = Colors.SELECTED if selected_entry == actual_index and in_focus else Colors.DEFAULT
                txtcolor = bgcolor

            self.draw_entry(title, current_y, box_height, box_width, i, bgcolor, txtcolor)
            current_y += box_height

        self._visible_entries_count = length

    @staticmethod
    def _calculate_visible_entry_count(available_height, total_entries, minimum, maximum, box_height):
        """Apply the configured entry limits within the available list height."""
        max_fit = available_height // box_height
        if minimum == -1:
            length = max_fit
            if maximum > 0:
                length = min(length, maximum)
        elif minimum > 0:
            max_actual = maximum if maximum > 0 else total_entries
            max_actual = max(max_actual, minimum)
            length = min(max(total_entries, minimum), max_fit, max_actual)
        else:
            max_actual = maximum if maximum > 0 else total_entries
            length = min(total_entries, max_fit, max_actual)
        return max(1, length)

    def draw_scrollbar(self, parent_win, scrollbar_win, height, total, visible_count, scroll_offset, y, x, in_focus):
        return draw_vertical_scrollbar(
            parent_win,
            scrollbar_win,
            height,
            total,
            visible_count,
            scroll_offset,
            y,
            x,
            in_focus,
        )

    def draw_entry(self, title, y, box_height, box_width, wid, bgcolor, txtcolor):
        while len(self._entries) <= wid:
            self._entries.append(None)

        if self._entries[wid] is None:
            win = Window(box_height, box_width, y, 0, 0, wid, self._entry_list)
            self._entries[wid] = win
        else:
            win = self._entries[wid]

        win.background = bgcolor
        win.draw_box()
        win.empty(len(title))
        win.write_animate(title.upper(), 1, 2, 0, txtcolor, True)
        win.refresh()

    def draw_content_window(self):
        if not self._content and self._entry_list:
            sidebar_spacing = Others.SCROLLBAR_PADDING
            height = self._explorer.height - self._header.height - self._footer.height - self._entry_list.height
            width = self._explorer.width - self._sidebar.width - Others.SCREEN_PADDING - sidebar_spacing
            y = self._entry_list.start_y + self._entry_list.height
            x = self._sidebar.width + sidebar_spacing
            self._content = Window(height, width, y, x, parent_window=self._explorer)
            self._content.draw_box()
            self._content.refresh()

    def display_text(self, lines, scroll_offset, in_focus):
        if not self._content:
            return

        if not self._content_inner and in_focus:
            self._content_inner = Window(self._content.height - 2, self._content.width - 3, 1, 1, parent_window=self._content)

        if self._content_inner and in_focus:
            self._content_inner.dump_log()
            self._content_inner.log_lines(lines)
            self._content_inner.render_log(scroll_offset)

        self._content_scrollbar = self.draw_scrollbar(self._content, self._content_scrollbar, self._content.height - 2, self.get_content_max_scroll(), 0, scroll_offset, 1, self._content.width - 2, in_focus)

    def clear_content(self):
        if not self._content:
            return
        else:
            self._content.empty()

        if not self._content_inner:
            return
        else:
            self._content_inner.empty()

        if not self._content_scrollbar:
            return
        else:
            self._content_scrollbar.empty()

        self._content.reload()

    def display_switch(self, state_labels, action_verbs, switch_selected, current_state):
        parent = self._content
        if not parent:
            return

        min_box_height = 3
        max_box_height = 5
        available_height = parent.height - Others.BORDER_PADDING
        box_height = max(min_box_height, min(max_box_height, available_height))

        text_spacing = 2
        min_box_width = 5
        longest_label = max(state_labels + action_verbs, key=len, default="")
        max_box_width = len(longest_label) + Others.BORDER_PADDING + text_spacing
        available_width = parent.width - Others.BORDER_PADDING
        box_width = max(min_box_width, min(max_box_width, (available_width // 2)))

        y, left_x = self._center_in_content(parent, box_width * 2, box_height)
        right_x = left_x + box_width

        if not self._switch_left:
            self._switch_left = Window(box_height, box_width, y, left_x, parent_window=parent)
        if not self._switch_right:
            self._switch_right = Window(box_height, box_width, y, right_x, parent_window=parent)

        if current_state:
            title_l = action_verbs[0]
            title_r = state_labels[1]
        else:
            title_l = state_labels[0]
            title_r = action_verbs[1]

        if switch_selected == 0:
            color_l = Colors.SELECTED
            color_r = Colors.DEFAULT
        else:
            color_l = Colors.DEFAULT
            color_r = Colors.SELECTED

        self._switch_left.background = color_l
        self._switch_right.background = color_r
        self._switch_left.draw_box()
        self._switch_right.draw_box()

        x_l = max(1, (box_width - len(title_l)) // 2)
        x_r = max(1, (box_width - len(title_r)) // 2)
        y_center = box_height // 2

        pad_l = box_width - 2
        pad_r = box_width - 2

        self._switch_left.clear_line(y_center - 1, 1, pad_l)
        self._switch_left.clear_line(y_center, 1, pad_l)
        self._switch_left.clear_line(y_center + 1, 1, pad_l)

        self._switch_right.clear_line(y_center - 1, 1, pad_r)
        self._switch_right.clear_line(y_center, 1, pad_r)
        self._switch_right.clear_line(y_center + 1, 1, pad_r)


        self._switch_left.write_simple(title_l.upper(), y_center, x_l, color_l, True)
        self._switch_right.write_simple(title_r.upper(), y_center, x_r, color_r, True)

    def display_button(self, state_labels, action_verbs, current_state):
        parent = self._content
        if not parent:
            return

        if current_state:
            label = state_labels[0]
            color = Colors.DEFAULT
        else:
            label = action_verbs[0]
            color = Colors.SELECTED

        min_box_height = 3
        max_box_height = 5
        text_spacing = 2
        min_box_width = len(label)

        available_height = parent.height - Others.BORDER_PADDING
        available_width = parent.width - Others.BORDER_PADDING

        box_height = max(min_box_height, min(max_box_height, available_height))

        max_box_width = len(label) + Others.BORDER_PADDING + text_spacing

        box_width = max(min_box_width, min(max_box_width, available_width))

        y, x = self._center_in_content(parent, box_width, box_height)

        if not self._button:
            self._button = Window(box_height, box_width, y, x, parent_window=parent)
        if self._button.height != box_height or self._button.width != box_width:
            self._button.background = Colors.DEFAULT
            self._button.clear()
            self._button.refresh()
            self._button.resize(box_height, box_width)

        self._button.background = color
        self._button.draw_box()

        x_l = max(1, (box_width - len(label)) // 2)
        y_center = box_height // 2

        pad_l = box_width - 2

        self._button.clear_line(y_center - 1, 1, pad_l)
        self._button.clear_line(y_center, 1, pad_l)
        self._button.clear_line(y_center + 1, 1, pad_l)

        self._button.write_simple(label.upper(), y_center, x_l, color, True)

    def display_audioplayer(self, is_playing, audio_length=0, elapsed_time=0):
        if not audio_length > 0:
            return

        parent = self._content
        if not parent:
            return

        box_height = 5
        spacing = 2

        available_width = parent.width - Others.BORDER_PADDING

        box_width = available_width // 3
        bar_width = box_width - Others.BORDER_PADDING - spacing

        y_box, x_box = self._center_in_content(parent, box_width, box_height)

        if not self._audioplayer:
            self._audioplayer = Window(box_height, box_width, y_box, x_box, parent_window=parent)

        self._audioplayer.background = Colors.DEFAULT
        self._audioplayer.draw_box()

        time_text = f"{self.format_time(elapsed_time)} / {self.format_time(audio_length)}"

        text_y = box_height // 2 + 1
        text_x = box_width // 2 - len(time_text) // 2

        progress = min(elapsed_time / audio_length, 1.0)

        filled = int(progress * bar_width)
        filled = max(0, min(filled, bar_width))

        remaining = max(0, bar_width - filled)

        bar_y = box_height // 2
        bar_x = box_width // 2 - bar_width // 2

        if is_playing:
            state = Tokens.PLAYING
        else:
            state = Tokens.PAUSED

        state_x = box_width // 2 - len(state) // 2

        self._audioplayer.clear_line(1, 1, box_width - 2)
        self._audioplayer.write_simple(state.upper(), 1, state_x, bold=True)
        self._audioplayer.write_simple(time_text, text_y, text_x, bold=True)
        self._audioplayer.write_simple("▬" * remaining, bar_y, bar_x + filled, Colors.DEFAULT)
        self._audioplayer.write_simple("▬" * (filled - 1) + "●", bar_y, bar_x, Colors.DEFAULT)

    def format_time(self, seconds):
        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{minutes:02}:{secs:02}"

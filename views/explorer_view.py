import curses

from views.terminal_view import TerminalView
import time
from .window import Window
from .popups import Messagebox, PasscodeBox
from core import Colors, Focus, Screens, Others, TokensDE

class ExplorerView(TerminalView):
    def __init__(self, stdscr):
        super().__init__(stdscr)
        self._header = None
        self._sidebar = None
        self._entry_list = None
        self._content = None
        self._sidebar_scrollbar = None
        self._entries_scrollbar = None
        self._categories = []
        self._entries = []
        self._visible_categories_count = 0
        self._visible_entries_count = 0

    def get_visible_categories_count(self):
        return self._visible_categories_count

    def get_visible_entries_count(self):
        return self._visible_entries_count

    def draw_header(self, title=""):
        if not self._header:
            self._header = Window(1, self._screen_width, 0, 0)
            self._header.background = Colors.SELECTED
            self._header.write_simple(title.upper(), y=0, x=1, color=Colors.SELECTED, bold=True)
            self._header.refresh()

    def draw_sidebar(self, categories, selected_category, category_scroll_offset, infocus):
        if not self._sidebar:
            height = (self._screen_height - self._header.height - self._footer.height - Others.SCREEN_PADDING)
            width = self._screen_width // 4 + Others.SCROLLBAR_PADDING
            self._sidebar = Window(height, width, self._header.start_y + 2, 1)
        self.draw_all_categories(categories, selected_category, category_scroll_offset, infocus)

    def draw_all_categories(self, categories, selected_category, category_scroll_offset, infocus):
        max_box_height = 8
        min_box_height = 5
        minimum_categories = Others.MINIMUM_CATEGORIES
        if Others.MAXIMUM_CATEGORIES < 0:
            maximum_categories = len(categories)
        else:
            maximum_categories = Others.MAXIMUM_CATEGORIES

        box_width = self._sidebar.width - Others.SCROLLBAR_PADDING
        available_height = self._sidebar.height - 1
        total_categories = len(categories)
        max_fit_by_min_height = available_height // min_box_height

        if maximum_categories > 0:
            max_fit_by_min_height = min(max_fit_by_min_height, maximum_categories)

        length = max(minimum_categories, max_fit_by_min_height)
        length = min(length, available_height // min_box_height)

        if maximum_categories > 0:
            length = min(length, maximum_categories)

        length = max(1, length)
        box_height = available_height // length
        box_height = max(min_box_height, min(box_height, max_box_height))
        possible_length = available_height // box_height

        if maximum_categories > 0:
            possible_length = min(possible_length, maximum_categories)

        length = max(minimum_categories, possible_length)
        self._visible_categories_count = length
        total_height = length * box_height
        y = max(0, self._sidebar.height - total_height)

        self._sidebar.write_simple(TokensDE.FOLDER.upper(), y - 1, 0)

        scroll_offset = category_scroll_offset
        max_scroll = max(0, total_categories - length)
        scroll_offset = min(scroll_offset, max_scroll)

        self.draw_sidebar_scrollbar(self._sidebar, total_height, total_categories, length, scroll_offset, y, self._sidebar.width - 1, infocus)

        while len(self._categories) < length:
            self._categories.append(None)

        for i in range(length):
            if y + box_height > self._sidebar.height:
                break

            actual_index = scroll_offset + i

            if actual_index >= total_categories:
                title = ""
                bgcolor = Colors.DEFAULT
                txtcolor = Colors.DEFAULT
            else:
                title = categories[actual_index].title

                if selected_category == actual_index:
                    bgcolor = Colors.SELECTED
                    txtcolor = Colors.SELECTED
                else:
                    bgcolor = Colors.DEFAULT
                    txtcolor = Colors.DEFAULT

            self.draw_category(title, y, box_height, box_width, i, bgcolor, txtcolor)

            y += box_height

    def draw_sidebar_scrollbar(self, sidebar_win, height, total_categories, visible_categories, scroll_offset, y, x, infocus):
        if not self._sidebar_scrollbar:
            self._sidebar_scrollbar = Window(height, 1, y, x, parent_window=sidebar_win)
        arrow_up = "△"
        arrow_down = "▽"
        up_y = 1
        down_y = height - 2
        can_scroll_up = scroll_offset > 0
        can_scroll_down = scroll_offset + visible_categories < total_categories
        if can_scroll_up:
            arrow_up = "▲"
        if can_scroll_down:
            arrow_down = "▼"
        if not can_scroll_up and not can_scroll_down or not infocus:
            arrow_up = " "
            arrow_down = " "
        self._sidebar_scrollbar.write_simple(arrow_up, up_y, 0)
        self._sidebar_scrollbar.write_simple(arrow_down, down_y, 0)
        self._sidebar_scrollbar.refresh()

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

    def draw_entry_list(self, category, selected_entry, entry_scroll_offset, infocus):
        box_height = 3
        if category:
            entries = category.entries
            if not self._entry_list:
                sidebar_spacing = Others.SCROLLBAR_PADDING
                height = self.calculate_entry_list_height(box_height, entries)
                width = ((self._screen_width - Others.SCREEN_PADDING) - self._sidebar.width - sidebar_spacing) //  3 * 2
                x = self._sidebar.width + sidebar_spacing
                self._entry_list = Window(height, width, self._header.start_y + 1, x)
            self.draw_all_entries(box_height, entries, selected_entry, entry_scroll_offset, infocus)

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

    def draw_all_entries(self, box_height, entries, selected_entry, entry_scroll_offset, infocus):
        minimum_entries = Others.MINIMUM_ENTRIES
        maximum_entries = Others.MAXIMUM_ENTRIES
        y = 2

        box_width = self._entry_list.width - Others.SCROLLBAR_PADDING
        available_height = self._entry_list.height - y
        total_entries = len(entries)
        possible_length = available_height // box_height

        if maximum_entries > 0:
            possible_length = min(possible_length, maximum_entries)

        length = max(minimum_entries, possible_length)
        length = max(1, length)

        self._visible_entries_count = length

        total_height = length * box_height

        scroll_offset = entry_scroll_offset
        max_scroll = max(0, total_entries - length)
        scroll_offset = min(scroll_offset, max_scroll)

        self._entry_list.write_simple(TokensDE.FILES.upper(), y - 1, 0)

        self.draw_entries_scrollbar(self._entry_list, total_height, total_entries, length, scroll_offset, y, self._entry_list.width - 1, infocus)

        while len(self._entries) < length:
            self._entries.append(None)

        current_y = y

        for i in range(length):
            if current_y + box_height > self._entry_list.height:
                break

            actual_index = scroll_offset + i

            if actual_index >= total_entries:
                title = ""
                bgcolor = Colors.DEFAULT
                txtcolor = Colors.DEFAULT
            else:
                title = entries[actual_index].title

                if selected_entry == actual_index and infocus:
                    bgcolor = Colors.SELECTED
                    txtcolor = Colors.SELECTED
                else:
                    bgcolor = Colors.DEFAULT
                    txtcolor = Colors.DEFAULT

            self.draw_entry(title, current_y, box_height, box_width, i, bgcolor, txtcolor)
            current_y += box_height

    def draw_entries_scrollbar(self, entries_win, height, total_entries, visible_entries_count, scroll_offset, y, x, infocus):
        try:
            if not self._entries_scrollbar:
                self._entries_scrollbar = Window(height, 1, y, x, parent_window=entries_win)

            if self._entries_scrollbar.height != height:
                self._entries_scrollbar.resize(height, 1)

            up_y = 1
            down_y = max(1, height - 2)

            can_scroll_up = scroll_offset > 0
            can_scroll_down = scroll_offset + visible_entries_count < total_entries

            scroll_needed = total_entries > visible_entries_count

            arrow_up = "△"
            arrow_down = "▽"

            if can_scroll_up:
                arrow_up = "▲"

            if can_scroll_down:
                arrow_down = "▼"

            if not scroll_needed or not infocus:
                arrow_up = " "
                arrow_down = " "

            self._entries_scrollbar.write_simple(arrow_up, up_y, 0)
            self._entries_scrollbar.write_simple(arrow_down, down_y, 0)

            self._entries_scrollbar.refresh()

        except curses.error:
            pass

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
            height = self._screen_height - self._header.height - self._footer.height - self._entry_list.height
            width = self._screen_width - self._sidebar.width - Others.SCREEN_PADDING - sidebar_spacing
            y = self._entry_list.start_y + self._entry_list.height + Others.SCREEN_PADDING
            x = self._sidebar.width + sidebar_spacing
            self._content = Window(height, width, y, x)
            self._content.draw_box()
            self._content.refresh()


    def display_text(self, lines, scroll_offset, infocus):
        if not self._content:
            return
        if self._content:
            if infocus:
                self._content.log_lines(lines)
                visible_lines = self._content.height - 2
                max_offset = max(0, len(self._content.log) - visible_lines)
                scroll_offset = max(0, min(scroll_offset, max_offset))
                self._content.render_log(scroll_offset)
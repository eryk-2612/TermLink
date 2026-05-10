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
            self._header = Window(1, self._screen_width - 2, 1, 1)
            self._header.background = Colors.SELECTED
            self._header.write_simple(title.upper(), y=0, x=1, color=Colors.SELECTED, bold=True)
            self._header.refresh()

    def draw_sidebar(self, categories, selected_category, category_scroll_offset):
        if not self._sidebar:
            height = (self._screen_height - self._header.height - self._footer.height - 2)
            width = self._screen_width // 5 + Others.SCROLLBAR_PADDING
            self._sidebar = Window(height, width, self._header.start_y + 2, 1)
        self.draw_all_categories(categories, selected_category, category_scroll_offset)

    def draw_all_categories(self, categories, selected_category, category_scroll_offset):
        max_box_height = 6
        min_box_height = 6
        minimum_categories = 1 # technically ignored
        maximum_categories = 4

        box_width = self._sidebar.width - Others.SCROLLBAR_PADDING
        available_height = self._sidebar.height - 1

        max_possible_length = available_height // min_box_height
        length = max(minimum_categories, max_possible_length)

        box_height = available_height // length
        box_height = max(min_box_height, min(box_height, max_box_height))

        length = available_height // box_height
        if length > maximum_categories:
            length = maximum_categories

        self._visible_categories_count = length

        total_height = length * box_height
        y = max(0, self._sidebar.height - total_height)

        self._sidebar.write_simple(TokensDE.FOLDER.upper(), y - 1, 0)

        scroll_offset = category_scroll_offset
        total_categories = len(categories)

        max_scroll = max(0, total_categories - length)
        scroll_offset = min(scroll_offset, max_scroll)

        self.draw_sidebar_scrollbar(self._sidebar, total_height, total_categories, length, scroll_offset, y, self._sidebar.width - 1)

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

            self.draw_category(title,y, box_height, box_width, i, bgcolor, txtcolor)
            y += box_height

    def draw_sidebar_scrollbar(self, sidebar_win, height, total_categories, visible_categories, scroll_offset, y, x):
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
        if not can_scroll_up and not can_scroll_down:
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
        if category:
            entries = category.entries
            if not self._entry_list:
                sidebar_spacing = Others.SCROLLBAR_PADDING
                height = self._screen_height // 4
                width = (self._screen_width - Others.SCREEN_PADDING) - self._sidebar.width - sidebar_spacing
                x = self._sidebar.width + sidebar_spacing
                self._entry_list = Window(height, width, self._header.start_y + 1, x)
            self.draw_all_entries(entries, selected_entry, entry_scroll_offset, infocus)

    def draw_all_entries(self, entries, selected_entry, entry_scroll_offset, infocus):
        min_box_height = 3
        minimum_entries = 1 # technically ignored
        maximum_entries = 3
        y = 2

        box_width = self._entry_list.width - Others.SCROLLBAR_PADDING
        available_height = self._entry_list.height - 1
        total_entries = len(entries)

        max_possible_length = available_height // min_box_height
        length = min(maximum_entries, max(minimum_entries, max_possible_length))
        box_height = min_box_height
        self._visible_entries_count = length
        total_height = length * box_height

        scroll_offset = entry_scroll_offset
        max_scroll = max(0, total_entries - length)
        scroll_offset = min(scroll_offset, max_scroll)

        self._entry_list.write_simple(TokensDE.FILES.upper(), y - 1, 0)
        self.draw_entries_scrollbar(self._entry_list, total_height, total_entries, length, scroll_offset, y, self._entry_list.width - 1)

        while len(self._entries) < length:
            self._entries.append(None)

        for i in range(length):
            if y + box_height > self._entry_list.height:
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

            self.draw_entry(title,y, box_height, box_width, i, bgcolor, txtcolor)
            y += box_height

    def draw_entries_scrollbar(self, entires_win, height, total_entries, visible_entries_count, scroll_offset, y, x):
        if not self._entries_scrollbar:
            self._entries_scrollbar = Window(height, 1, y, x, parent_window=entires_win)
        arrow_up = "△"
        arrow_down = "▽"
        up_y = 1
        down_y = height - 2
        can_scroll_up = scroll_offset > 0
        can_scroll_down = scroll_offset + visible_entries_count < total_entries
        if can_scroll_up:
            arrow_up = "▲"
        if can_scroll_down:
            arrow_down = "▼"
        if not can_scroll_up and not can_scroll_down:
            arrow_up = " "
            arrow_down = " "
        self._entries_scrollbar.write_simple(arrow_up, up_y, 0)
        self._entries_scrollbar.write_simple(arrow_down, down_y, 0)
        self._entries_scrollbar.refresh()

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
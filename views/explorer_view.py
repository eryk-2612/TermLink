from views.terminal_view import TerminalView
from .window import Window
from core import Colors, Focus, Screens, Others, TokensDE

class ExplorerView(TerminalView):
    def __init__(self, stdscr):
        super().__init__(stdscr)
        self._header = None
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
        self._categories = []
        self._entries = []
        self._visible_categories_count = 0
        self._visible_entries_count = 0

    @property
    def sidebar_window(self):
        return self._sidebar

    @property
    def entry_list_window(self):
        return self._entry_list

    @property
    def content_window(self):
        return self._content

    def get_visible_categories_count(self):
        return self._visible_categories_count

    def get_visible_entries_count(self):
        return self._visible_entries_count

    def get_content_max_scroll(self):
        if not self._content_inner:
            return 0
        return self._content_inner.get_max_scroll_offset()

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

        self._sidebar_scrollbar = self.draw_scrollbar(self._sidebar, self._sidebar_scrollbar, total_height, total_categories, length, scroll_offset, y, self._sidebar.width - 1, infocus)

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

                if selected_category == actual_index and infocus:
                    bgcolor = Colors.SELECTED
                    txtcolor = Colors.SELECTED
                else:
                    bgcolor = Colors.DEFAULT
                    txtcolor = Colors.DEFAULT

            self.draw_category(title, y, box_height, box_width, i, bgcolor, txtcolor)

            y += box_height

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

        self._entries_scrollbar = self.draw_scrollbar(self._entry_list, self._entries_scrollbar, total_height, total_entries, length, scroll_offset, y, self._entry_list.width - 1, infocus)

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

    def draw_scrollbar(self, parent_win, scrollbar_win, height, total, visible_count, scroll_offset, y, x, infocus):
        if not scrollbar_win:
            scrollbar_win = Window(height, 1, y, x, parent_window=parent_win)

        up_y = 1
        down_y = max(1, height - 2)

        can_scroll_up = scroll_offset > 0
        can_scroll_down = scroll_offset + visible_count < total

        scroll_needed = total > visible_count

        arrow_up = "△"
        arrow_down = "▽"

        if can_scroll_up:
            arrow_up = "▲"

        if can_scroll_down:
            arrow_down = "▼"

        if not scroll_needed or not infocus:
            arrow_up = " "
            arrow_down = " "

        if up_y == down_y:
            if can_scroll_up:
                scrollbar_win.write_simple(arrow_up, up_y, 0)
            elif can_scroll_down:
                scrollbar_win.write_simple(arrow_down, down_y, 0)
        else:
            scrollbar_win.write_simple(arrow_up, up_y, 0)
            scrollbar_win.write_simple(arrow_down, down_y, 0)
        return scrollbar_win

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
            y = self._entry_list.start_y + self._entry_list.height
            x = self._sidebar.width + sidebar_spacing
            self._content = Window(height, width, y, x)
            self._content.draw_box()
            self._content.refresh()

    def display_text(self, lines, scroll_offset, infocus):
        if not self._content:
            return

        if not self._content_inner and infocus:
            self._content_inner = Window(self._content.height - 2, self._content.width - 3, 1, 1, parent_window=self._content)

        if self._content_inner and infocus:
            self._content_inner.dump_log()
            self._content_inner.log_lines(lines)
            self._content_inner.render_log(scroll_offset)

        self._content_scrollbar = self.draw_scrollbar(self._content, self._content_scrollbar, self._content.height - 2, self.get_content_max_scroll(), 0, scroll_offset, 1, self._content.width - 2, infocus)

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

        y = (available_height // 2) - (box_height // 2)
        left_x = (available_width // 2) - box_width
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

        y = (available_height // 2) - (box_height // 2)
        x = (available_width // 2) - (box_width // 2)

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

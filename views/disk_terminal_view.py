import curses

from core import Colors, Tokens
from .window import Window


class DiskTerminalView:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.window = Window(self.height, self.width, 0, 0)
        self._selection_names = None
        self._selection_index = None
        self._selection_first = None

    def draw_message(self, message, detail=None):
        self.window.clear()
        lines = [message]
        if detail:
            lines.append(detail)
        start_y = max(0, self.height // 2 - len(lines) // 2)
        for index, line in enumerate(lines):
            text = line[:max(0, self.width - 2)]
            x = max(0, (self.width - len(text)) // 2)
            try:
                self.window.write_simple(text, start_y + index, x, Colors.DEFAULT, index == 0)
            except curses.error:
                pass
        self.window.refresh()

    def draw_file_selection(self, filenames, selected_index):
        visible_count = max(1, self.height - 4)
        first = min(max(0, selected_index - visible_count + 1), max(0, len(filenames) - visible_count))
        names = tuple(filenames)

        if names == self._selection_names and first == self._selection_first:
            if selected_index == self._selection_index:
                return
            if self._selection_index is not None:
                self._draw_selection_row(filenames, self._selection_index, first, visible_count, selected_index)
            self._draw_selection_row(filenames, selected_index, first, visible_count, selected_index)
            self._selection_index = selected_index
            return

        self.window.clear()
        heading = Tokens.FLOPPY_SELECT_TERMINAL
        x = max(0, (self.width - len(heading)) // 2)
        try:
            self.window.write_simple(heading, 1, x, Colors.DEFAULT, True)
        except curses.error:
            pass

        for index in range(first, min(first + visible_count, len(filenames))):
            self._draw_selection_row(filenames, index, first, visible_count, selected_index)

        footer = Tokens.FLOPPY_SELECT_HINT
        footer_x = max(0, (self.width - len(footer)) // 2)
        try:
            self.window.write_simple(footer[:max(0, self.width - 2)], max(0, self.height - 2), footer_x)
        except curses.error:
            pass
        self.window.refresh()
        self._selection_names = names
        self._selection_index = selected_index
        self._selection_first = first

    def _draw_selection_row(self, filenames, index, first, visible_count, selected_index):
        if index < first or index >= min(first + visible_count, len(filenames)):
            return
        text = filenames[index][:max(0, self.width - 4)]
        x = max(0, (self.width - len(text)) // 2)
        row = index - first + 3
        selected = index == selected_index
        try:
            self.window.write_simple(text, row, x, Colors.SELECTED if selected else Colors.DEFAULT, selected)
        except curses.error:
            pass

import curses

from core import Colors, Tokens
from .window import Window


class DiskTerminalView:
    """Draw the disk-loading prompt, errors, and terminal selection screen."""

    def __init__(self, stdscr):
        """Create a full-screen window and initialize render-state caches."""
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.window = Window(self.height, self.width, 0, 0)
        self._selection_names = None
        self._selection_index = None
        self._selection_first = None
        self._message_state = None

    def draw_message(self, message, detail=None):
        """Display a centered status message only when its contents change."""
        message_state = (message, detail)
        # Preserve the current screen when the message has not changed.
        if message_state == self._message_state:
            return

        self.window.clear()
        self._selection_names = None
        self._selection_index = None
        self._selection_first = None
        lines = [message]
        if detail:
            lines.append(detail)
        start_y = max(0, self.height // 2 - len(lines) // 2)
        for index, line in enumerate(lines):
            text = line[:max(0, self.width - 2)]
            x = max(0, (self.width - len(text)) // 2)
            try:
                attributes = curses.color_pair(Colors.DEFAULT)
                if index == 0:
                    attributes |= curses.A_BOLD
                self.window.win.addstr(start_y + index, x, text, attributes)
            except curses.error:
                pass
        self.window.refresh()
        self._message_state = message_state

    def draw_file_selection(self, filenames, selected_index):
        """Draw a centered, scrollable list and update only changed selection rows."""
        # Center the heading and visible program list as a single block.
        visible_count = max(1, self.height - 4)
        shown_count = min(len(filenames), visible_count)
        content_height = shown_count + 2
        start_y = max(0, (self.height - content_height) // 2)
        row_start = start_y + 2
        first = min(max(0, selected_index - visible_count + 1), max(0, len(filenames) - visible_count))
        names = tuple(filenames)

        if names == self._selection_names and first == self._selection_first:
            if selected_index == self._selection_index:
                return
            # Redraw only the old and new selected rows while the list stays in place.
            if self._selection_index is not None:
                self._draw_selection_row(filenames, self._selection_index, first, visible_count, row_start, selected_index)
            self._draw_selection_row(filenames, selected_index, first, visible_count, row_start, selected_index)
            self._selection_index = selected_index
            self.window.refresh()
            return

        self.window.clear()
        self._message_state = None
        heading = Tokens.FLOPPY_SELECT_TERMINAL
        x = max(0, (self.width - len(heading)) // 2)
        try:
            self.window.win.addstr(start_y, x, heading, curses.color_pair(Colors.DEFAULT) | curses.A_BOLD)
        except curses.error:
            pass

        for index in range(first, min(first + visible_count, len(filenames))):
            self._draw_selection_row(filenames, index, first, visible_count, row_start, selected_index)
        self.window.refresh()
        self._selection_names = names
        self._selection_index = selected_index
        self._selection_first = first

    def _draw_selection_row(self, filenames, index, first, visible_count, row_start, selected_index):
        """Draw one visible program row with its selected state."""
        if index < first or index >= min(first + visible_count, len(filenames)):
            return
        text = filenames[index][:max(0, self.width - 4)]
        x = max(0, (self.width - len(text)) // 2)
        row = index - first + row_start
        selected = index == selected_index
        color = Colors.SELECTED if selected else Colors.DEFAULT
        attributes = curses.color_pair(color) | (curses.A_BOLD if selected else 0)
        try:
            self.window.win.addstr(row, x, text, attributes)
        except curses.error:
            pass

import curses

from core import Colors, Tokens
from .window import Window
from .render_models import DiskFrame


class DiskTerminalView:
    """Draw the disk-loading prompt, errors, and terminal selection screen."""

    def __init__(self, stdscr):
        """Create a full-screen window and initialize render-state caches."""
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.window = Window(self.height, self.width, 0, 0)
        self._header = None
        self._selection_names = None
        self._selection_index = None
        self._selection_first = None
        self._selection_x = 0
        self._selection_label_width = 0
        self._message_state = None

    def draw_message(self, message, detail=None):
        """Display a centered status message only when its contents change."""
        message_state = (message, detail)
        # Preserve the current screen when the message has not changed.
        if message_state == self._message_state:
            return

        self.window.clear()
        self.draw_dialog_header()
        self._selection_names = None
        self._selection_index = None
        self._selection_first = None
        lines = [message[:max(0, self.width - 2)]]
        if detail:
            lines.append(detail[:max(0, self.width - 2)])
        start_y = max(1, 1 + (self.height - 1 - len(lines)) // 2)
        for index, line in enumerate(lines):
            text = line[:max(0, self.width - 2)]
            x = max(0, (self.width - len(text)) // 2)
            try:
                attributes = self.window.text_attributes(
                    Colors.DEFAULT, bold=index == 0
                )
                self.window.win.addstr(start_y + index, x, text, attributes)
            except curses.error:
                pass
        self.window.refresh()
        self._message_state = message_state

    def read_key(self):
        return self.stdscr.getch()

    def render(self, frame: DiskFrame):
        if frame.mode == "select":
            self.draw_file_selection(frame.filenames, frame.selected_index)
        else:
            self.draw_message(frame.message, frame.detail or None)

    def draw_file_selection(self, filenames, selected_index):
        """Draw a centered, left-aligned menu and update changed selection rows."""
        visible_count = max(1, self.height - 4)
        shown_count = min(len(filenames), visible_count)
        content_height = shown_count + 2
        start_y = max(1, 1 + (self.height - 2 - content_height) // 2)
        row_start = start_y + 2
        first = min(max(0, selected_index - visible_count + 1), max(0, len(filenames) - visible_count))
        names = tuple(filenames)
        heading = Tokens.FLOPPY_SELECT_TERMINAL
        longest = max([len(heading), *(len(name) for name in filenames)])
        block_width = min(max(0, self.width - 2), longest + 2)
        self._selection_x = max(0, (self.width - block_width) // 2)
        self._selection_label_width = max(0, self.width - self._selection_x - 3)

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
        self.draw_dialog_header()
        self._add_clipped(
            start_y, self._selection_x + 2, heading.upper(),
            curses.color_pair(Colors.DEFAULT) | curses.A_BOLD,
        )

        for index in range(first, min(first + visible_count, len(filenames))):
            self._draw_selection_row(filenames, index, first, visible_count, row_start, selected_index)
        if self.height >= 3:
            hint = Tokens.DISK_MENU_HINT
            hint_x = max(1, (self.width - len(hint)) // 2)
            self._add_clipped(
                self.height - 1, hint_x, hint, curses.color_pair(Colors.DEFAULT)
            )
        self.window.refresh()
        self._selection_names = names
        self._selection_index = selected_index
        self._selection_first = first

    def draw_dialog_header(self):
        if self._header is None:
            self._header = Window(1, self.width, 0, 0, parent_window=self.window)
        self._header.background = Colors.SELECTED
        self._header.win.erase()
        title = Tokens.LOAD_FROM_DISK.upper()[:max(0, self.width - 2)]
        try:
            self._header.write_simple(title, y=0, x=1, color=Colors.SELECTED, bold=True)
        except curses.error:
            pass
        self._header.refresh()

    def _draw_selection_row(self, filenames, index, first, visible_count, row_start, selected_index):
        """Draw one visible program row with its selected state."""
        if index < first or index >= min(first + visible_count, len(filenames)):
            return
        text = filenames[index][:self._selection_label_width]
        row = index - first + row_start
        selected = index == selected_index
        attributes = self.window.text_attributes(Colors.DEFAULT, bold=selected)
        prefix = "> " if selected else "  "
        self._add_clipped(row, self._selection_x, prefix + text, attributes)

    def _add_clipped(self, row, x, text, attributes):
        if row < 0 or row >= self.height or x >= self.width:
            return
        text = text[:max(0, self.width - x - 1)]
        if not text:
            return
        try:
            self.window.win.addstr(row, x, text, attributes)
        except curses.error:
            pass

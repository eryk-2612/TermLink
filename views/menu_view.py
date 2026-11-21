import curses

from core import Colors


class MenuView:
    def __init__(self, stdscr, height, width):
        self.stdscr = stdscr
        self.height = height
        self.width = width

    def render(self, labels, selected_index):
        """Draw menu labels without making selection or navigation decisions."""
        self.stdscr.erase()
        for index, label in enumerate(labels):
            x = self.width // 2 - len(label) // 2
            y = self.height // 2 - len(labels) // 2 + index
            selected = index == selected_index
            attributes = curses.color_pair(Colors.SELECTED if selected else Colors.DEFAULT)
            if selected:
                attributes |= curses.A_BOLD
            try:
                self.stdscr.addstr(y, x, label, attributes)
            except curses.error:
                pass
        self.stdscr.refresh()

    def read_key(self):
        return self.stdscr.getch()

    def clear(self):
        self.stdscr.erase()
        self.stdscr.refresh()

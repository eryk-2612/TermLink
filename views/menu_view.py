import curses

from core import Colors, Tokens


class MenuView:
    def __init__(self, stdscr, height, width):
        self.stdscr = stdscr
        self.height = height
        self.width = width

    def render(self, labels, selected_index):
        """Draw the centered logo and a bottom-left, marker-based menu."""
        self.stdscr.erase()

        logo = Tokens.LOGO
        top_gap = max(1, min(3, (self.height - len(logo)) // 8))
        logo_y = top_gap
        for index, line in enumerate(logo):
            x = max(0, (self.width - len(line)) // 2)
            try:
                self.stdscr.addstr(
                    logo_y + index, x, line,
                    curses.color_pair(Colors.DEFAULT) | curses.A_BOLD,
                )
            except curses.error:
                pass

        title_y = max(0, self.height - len(labels) - 3)
        try:
            self.stdscr.addstr(
                title_y, 3, Tokens.MAIN_MENU,
                curses.color_pair(Colors.DEFAULT) | curses.A_BOLD,
            )
        except curses.error:
            pass

        menu_y = title_y + 2
        for index, label in enumerate(labels):
            x = 1
            y = menu_y + index
            selected = index == selected_index
            attributes = curses.color_pair(Colors.DEFAULT)
            if selected:
                attributes |= curses.A_BOLD
            try:
                self.stdscr.addstr(y, x, f"> {label}" if selected else f"  {label}", attributes)
            except curses.error:
                pass
        self.stdscr.refresh()

    def read_key(self):
        return self.stdscr.getch()

    def clear(self):
        self.stdscr.erase()
        self.stdscr.refresh()

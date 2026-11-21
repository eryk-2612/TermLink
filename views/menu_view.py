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
        logo_bottom = logo_y + len(logo)
        menu_top = max(0, self.height - len(labels) - 3)
        # On short screens, keep the menu readable and omit the logo if both
        # blocks cannot fit without colliding.
        draw_logo = logo_bottom < menu_top - 1
        if draw_logo:
            for index, line in enumerate(logo):
                x = max(0, (self.width - len(line)) // 2)
                self._add_clipped(logo_y + index, x, line,
                                  curses.color_pair(Colors.DEFAULT) | curses.A_BOLD)

        title_y = menu_top
        self._add_clipped(title_y, 3, Tokens.MAIN_MENU,
                          curses.color_pair(Colors.DEFAULT) | curses.A_BOLD)

        menu_y = title_y + 2
        for index, label in enumerate(labels):
            x = 1
            y = menu_y + index
            selected = index == selected_index
            attributes = curses.color_pair(Colors.DEFAULT)
            if selected:
                attributes |= curses.A_BOLD
            self._add_clipped(y, x, f"> {label}" if selected else f"  {label}", attributes)

        if self.height >= 4:
            hint = Tokens.MENU_HINT
            hint_x = max(1, (self.width - len(hint)) // 2)
            self._add_clipped(self.height - 1, hint_x, hint,
                              curses.color_pair(Colors.DEFAULT))
        self.stdscr.refresh()

    def _add_clipped(self, y, x, text, attributes):
        if y < 0 or y >= self.height or x >= self.width:
            return
        text = text[:max(0, self.width - x - 1)]
        if not text:
            return
        try:
            self.stdscr.addstr(y, x, text, attributes)
        except curses.error:
            pass

    def read_key(self):
        return self.stdscr.getch()

    def clear(self):
        self.stdscr.erase()
        self.stdscr.refresh()

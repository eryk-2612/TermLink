from views.terminal_view import TerminalView
import time
from .window import Window
from .popups import Messagebox, PasscodeBox
from core import Colors, Focus, Screens, Others, TokensDE


class ExplorerView(TerminalView):
    def __init__(self, stdscr):
        super().__init__(stdscr)
        self._header = None
        self._categories_Window = None
        self._entries_window = None
        self._content_window = None

    def draw_all_categories(self, categories, state):
        box_width = self._categories_Window.width // 4
        length = max(len(categories), 4)

        optimal_height = self._categories_Window.height // ((length + 2) // 3)
        box_height = max(3, min(optimal_height, 6))

        total_height = length * box_height
        y = max(0, self._categories_Window.height - total_height)

        self._categories_Window.write_simple(TokensDE.FOLDER.upper(), y - 1, 0)

        for i in range(length):
            if y + box_height > self._categories_Window.height:
                break

            win = Window(box_height, box_width, y, 0, 0, i, self._categories_Window)

            if state.selected_category == i:
                bgcolor = Colors.SELECTED
                txtcolor = Colors.SELECTED
            else:
                bgcolor = Colors.DEFAULT
                txtcolor = Colors.TEXT

            title = categories[i].title if i < len(categories) else ""

            self.display_category(title, bgcolor, txtcolor, win)

            y += box_height

    def display_category(self, title, bgcolor, txtcolor, window):
        window.background = bgcolor
        window.draw_box()
        window.write_animate(title.upper(), 1, 2, 0, txtcolor, True)
        window.refresh()

    def draw_header(self, title=""):
        if not self._header:
            self._header = Window(1, self._screen_width - 2, 1, 1)
            self._header.background = Colors.INVERTED
            self._header.write_simple(title.upper(), y=0, x=1, color=Colors.SELECTED, bold=True)
            self._header.refresh()

    def draw_categories_window(self):
        if not self._categories_Window:
            height = (self._screen_height - self._header.height - self._footer.height - 2)
            width = self._screen_width - 2
            self._categories_Window = Window(height, width, self._header.start_y + 2, 1)
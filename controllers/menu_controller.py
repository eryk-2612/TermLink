import curses

from core import Tokens
from views.menu_view import MenuView


class MenuController:
    def __init__(self, stdscr, height, width, terminals):
        self.view = MenuView(stdscr, height, width)
        self.items = terminals + [Tokens.LOAD_FROM_DISK, Tokens.LEAVE]
        self.selected_index = 0

    def run(self):
        # The controller owns selection; MenuView owns curses drawing and input.
        labels = [
            item.upper() if isinstance(item, str) else item.model.name.upper()
            for item in self.items
        ]
        while True:
            self.view.render(labels, self.selected_index)
            key = self.view.read_key()
            if key == curses.KEY_UP:
                self.selected_index = (self.selected_index - 1) % len(self.items)
            elif key == curses.KEY_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.items)
            elif key in (10, 13, curses.KEY_ENTER):
                selected = self.items[self.selected_index]
                self.view.clear()
                return None if selected == Tokens.LEAVE else selected

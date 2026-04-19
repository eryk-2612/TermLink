import time
from views import Window, Messagebox, PasscodeBox
from core import Colors

class TerminalView:
    def __init__(self, stdscr):
        self._stdscr = stdscr
        self._screen_height, self._screen_width = self._stdscr.getmaxyx()

        startup_screen_height = self._screen_height
        startup_screen_width = self._screen_width
        startup_screen_y = self._screen_height // 2 - startup_screen_height // 2
        startup_screen_x = self._screen_width // 2 - startup_screen_width // 2

        self.startup_screen = Window(startup_screen_height - 1, startup_screen_width, startup_screen_y, startup_screen_x)

        self._footer = None
        self._header = None
        self._signin = None

    def draw_header(self, title):
        self._header = Window(1, self._screen_width - 2, 1, 1)
        self._header.background = Colors.INVERTED
        self._header.write_animate(title.upper(), y=0, x=1, color=Colors.SELECTED, bold=True)
        self._header.refresh()

    # (C) Terminal Systems
    def draw_footer(self, text=""):
        if not self._footer:
            self._footer = Window(1, self._screen_width - 2, self._screen_height - 1, 1)
            self._footer.background = Colors.DEFAULT
            x = self._footer.width // 2 - len(text) // 2  # x-Position so, dass der Text mittig ist
            self._footer.write_animate(text, y=0, x=x, color=Colors.DEFAULT)
            self._footer.refresh()

    def draw_lock(self, code, parent_window):
        passcodebox = PasscodeBox(parent_window, len(code))
        passcodebox.draw()
        passcodebox.refresh()
        return passcodebox

    def draw_messagebox(self, text, color, parent_window):
        parent_window.reload()
        messagebox = Messagebox(parent_window,text, color)
        messagebox.draw()
        parent_window.reload()

    def draw_startup_animation(self, parent_window, logo):
        logo_height = len(logo)
        logo_width = max(len(line) for line in logo)
        bar_length = logo_width

        # Fenstergröße: Logo + Ladebalken + bisschen Padding
        win_height = parent_window.height
        win_width = parent_window.width

        # Gesamtblock (Logo + Ladebalken)
        total_height = logo_height + 2

        # Zentriert
        start_y = win_height // 2 - total_height // 2
        start_x = win_width // 2 - logo_width // 2

        # Logo zeichnen
        for i, line in enumerate(logo):
            parent_window.write_simple(line, y=start_y + i, x=start_x, color=Colors.DEFAULT, bold=True)
            parent_window.refresh()
            time.sleep(0.35)

        # Ladebalken (unter dem Logo)
        bar_y = start_y + logo_height + 1
        bar_x = win_width // 2 - logo_width // 2

        for i in range(bar_length + 1):
            parent_window.write_simple(" " * i, bar_y, bar_x, Colors.INVERTED)
            parent_window.write_simple(" " * (bar_length - i), bar_y, bar_x + i, Colors.DEFAULT)
            parent_window.refresh()
            time.sleep(0.02)

        time.sleep(1)

        parent_window.reload()

    def draw_signin(self, parent_window, image, undraw=False):
        image_height = len(image)
        image_width = max(len(line) for line in image)

        if not self._signin:
            self._signin = Window(self._screen_height, self._screen_width, 0, 0)

        start_y = self._screen_height // 2 - image_height // 2
        start_x = self._screen_width // 2 - image_width // 2

        for i, line in enumerate(image):
            if undraw:
                self._signin.write_simple(" " * len(line), y=start_y + i, x=start_x, color=Colors.DEFAULT, bold=True)
            else:
                self._signin.write_simple(line, y=start_y + i, x=start_x, color=Colors.SELECTED, bold=True)

            self._signin.refresh()
            time.sleep(0.1)

        if undraw:
            parent_window.reload()
            self._signin = None
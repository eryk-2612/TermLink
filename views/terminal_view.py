from .window import Window
from .popups import Messagebox, PasscodeBox
from core import Colors
import time

class TerminalView:
    def __init__(self, stdscr):
        self._stdscr = stdscr
        self._screen_height, self._screen_width = self._stdscr.getmaxyx()
        self._footer = None
        self._header = None
        self._fullscreen = None
        self._passcodebox = None
        self._messagebox = None
        self._signin = None
        self._startup = None

    @property
    def signin_window(self):
        return self._signin

    @property
    def passcode_window(self):
        return self._passcodebox

    @property
    def messagebox_window(self):
        return self._messagebox

    @property
    def footer_window(self):
        return self._footer

    @property
    def header_window(self):
        return self._header

    @property
    def startup_window(self):
        return self._startup

    @property
    def fullscreen_window(self):
        if not self._fullscreen:
            startup_screen_height = self._screen_height
            startup_screen_width = self._screen_width
            startup_screen_y = self._screen_height // 2 - startup_screen_height // 2
            startup_screen_x = self._screen_width // 2 - startup_screen_width // 2
            self._fullscreen = Window(startup_screen_height, startup_screen_width, startup_screen_y, startup_screen_x)
        return self._fullscreen

    def draw_footer(self, text, parent):
        if not self._footer:
            if parent is not None:
                height = parent.height - 1
                width = parent.width
            else:
                height = self._screen_height - 1
                width = self._screen_width

            self._footer = Window(1, width, height, 0, parent_window=parent)
            self._footer.background = Colors.DEFAULT
            x = self._footer.width // 2 - len(text) // 2  # x-Position so, dass der Text mittig ist
            self._footer.write_simple(text, y=0, x=x, color=Colors.DEFAULT)
            self._footer.refresh()

    def draw_lock(self, code, parent_window, entered_code):
        self._passcodebox = PasscodeBox(parent_window, len(code))
        self._passcodebox.draw(entered_code)

    def destroy_lock(self):
        if self._passcodebox:
            self._passcodebox.undraw()
            self._passcodebox = None

    def draw_messagebox(self, text, color, parent_window):
        if self._messagebox is None:
            self._messagebox = Messagebox(parent_window, text, color)
            self._messagebox.draw()

    def undraw_messagebox(self):
        if self._messagebox:
            self._messagebox.undraw()
            self._messagebox = None

    def create_startup(self):
        if self._startup:
            return
        self._startup = Window(self._screen_height - self._footer.height, self._screen_width, 0, 0)

    def draw_startup_logo(self, logo):
        if not self._startup:
            return

        logo_height = len(logo)
        logo_width = max(len(line) for line in logo)

        total_height = logo_height + 2

        start_y = self._screen_height // 2 - total_height // 2
        start_x = self._screen_width // 2 - logo_width // 2

        for i, line in enumerate(logo):
            self._startup.write_simple(line, y=start_y + i, x=start_x, color=Colors.DEFAULT, bold=True)
            self._startup.refresh()
            time.sleep(0.35)

    def draw_startup_progressbar(self, logo, progress):
        if not self._startup:
            return

        logo_height = len(logo)
        logo_width = max(len(line) for line in logo)
        bar_length = logo_width

        total_height = logo_height + 2

        start_y = self._startup.height // 2 - total_height // 2

        bar_y = start_y + logo_height + 1
        bar_x = self._startup.width // 2 - logo_width // 2

        progress = max(0, min(100, progress))
        filled = int((logo_width * progress) / 100)

        for i in range(bar_length + 1):
            if i >= filled:
                break
            self._startup.write_simple(" " * i, bar_y, bar_x, Colors.SELECTED)
            # self._startup.write_simple(" " * (bar_length - i), bar_y, bar_x + i, Colors.DEFAULT)
            self._startup.refresh()
            time.sleep(0.02)

    def clean_up_startup_animation(self):
        if self._startup:
            time.sleep(1)
            self._startup.reload()
            self._startup = None
            self._footer = None

    def draw_signin(self, image=""):
        image_height = len(image)
        image_width = max(len(line) for line in image)

        start_y = self._screen_height // 2 - image_height // 2
        start_x = self._screen_width // 2 - image_width // 2

        if self._signin is None:
            self._signin = Window(self._screen_height, self._screen_width, 0, 0)
            self._signin.background = Colors.DEFAULT

        for i, line in enumerate(image):
            self._signin.write_simple(line, y=start_y + i, x=start_x, color=Colors.SELECTED, bold=True)
            self._signin.refresh()
            time.sleep(0.1)

    def undraw_signin(self, image=""):
        if self._signin:
            image_height = len(image)
            image_width = max(len(line) for line in image)

            start_y = self._signin.height // 2 - image_height // 2
            start_x = self._signin.width // 2 - image_width // 2

            for i, line in enumerate(image):
                self._signin.write_simple(" " * len(line), y=start_y + i, x=start_x, color=Colors.DEFAULT, bold=True)
                self._signin.refresh()
                time.sleep(0.1)

            del self._signin
            self._signin = None


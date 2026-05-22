import time
from .window import Window
from .popups import Messagebox, PasscodeBox
from core import Colors, Focus, Screens, Popups

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

    def get_window(self, requested_window=None):
        if requested_window:
            if requested_window == Screens.SIGNIN:
                return self._signin
            elif requested_window == Popups.MSG:
                return self._messagebox
            elif requested_window == Popups.LOCK:
                return self._passcodebox
        return self._get_fullscreen()

    def _get_fullscreen(self):
        if not self._fullscreen:
            startup_screen_height = self._screen_height
            startup_screen_width = self._screen_width
            startup_screen_y = self._screen_height // 2 - startup_screen_height // 2
            startup_screen_x = self._screen_width // 2 - startup_screen_width // 2
            self._fullscreen = Window(startup_screen_height - 1, startup_screen_width, startup_screen_y, startup_screen_x)
        return self._fullscreen

    # (C) Terminal Systems
    def draw_footer(self, text=""):
        if not self._footer:
            self._footer = Window(1, self._screen_width, self._screen_height - 1, 0)
            self._footer.background = Colors.DEFAULT
            x = self._footer.width // 2 - len(text) // 2  # x-Position so, dass der Text mittig ist
            self._footer.write_animate(text, y=0, x=x, color=Colors.DEFAULT)
            self._footer.refresh()

    def create_lock(self, code, parent_window):
        self._passcodebox = PasscodeBox(parent_window, len(code))

    def draw_lock(self, entered_code):
        if self._passcodebox:
            self._passcodebox.draw(entered_code)

    def destroy_lock(self):
        if self._passcodebox:
            self._passcodebox.destroy()

    def create_messagebox(self, text, color, parent_window, duration=1.5):
        self._messagebox = Messagebox(parent_window,text, color, duration)

    def draw_messagebox(self):
        if self._messagebox:
            self._messagebox.draw()

    def destroy_messagebox(self):
        if self._messagebox:
            self._messagebox.destroy()
            self._messagebox = None

    def skip_messagebox(self):
        if self._messagebox:
            self._messagebox.skip()

    @property
    def messagebox_finished(self):
        if self._messagebox:
            if self._messagebox.drawn:
                return not self._messagebox.visible
            else:
                return False
        else:
            return True

    def draw_startup_animation(self, parent_window, logo):
        logo_height = len(logo)
        logo_width = max(len(line) for line in logo)
        bar_length = logo_width

        startup = Window(self._screen_height - self._footer.height, self._screen_width, 0, 0)

        win_height = parent_window.height
        win_width = parent_window.width

        total_height = logo_height + 2

        start_y = win_height // 2 - total_height // 2
        start_x = win_width // 2 - logo_width // 2

        for i, line in enumerate(logo):
            startup.write_simple(line, y=start_y + i, x=start_x, color=Colors.DEFAULT, bold=True)
            startup.refresh()
            time.sleep(0.35)

        bar_y = start_y + logo_height + 1
        bar_x = win_width // 2 - logo_width // 2

        for i in range(bar_length + 1):
            startup.write_simple(" " * i, bar_y, bar_x, Colors.SELECTED)
            startup.write_simple(" " * (bar_length - i), bar_y, bar_x + i, Colors.DEFAULT)
            startup.refresh()
            time.sleep(0.02)

        time.sleep(1)
        parent_window.reload()
        del startup

    def draw_signin(self, parent, image=""):
        image_height = len(image)
        image_width = max(len(line) for line in image)

        start_y = parent.height // 2 - image_height // 2
        start_x = parent.width // 2 - image_width // 2

        if self._signin is None:
            self._signin = Window(self._screen_height -1, self._screen_width, 0, 0)
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



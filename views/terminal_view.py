from .window import Window
from .popups import Messagebox, PasscodeBox
from core import Colors
import curses
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
        self._startup_logo_drawn = False

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

    def read_key(self, target="fullscreen"):
        """Read a key without exposing the underlying curses window."""
        if target == "signin":
            window = self._signin
        elif target == "boot":
            window = self._startup
        elif target == "lock":
            window = self._passcodebox
        else:
            window = self.fullscreen_window
        return window.win.getch() if window else None

    def render(self, frame):
        """Render the shared sign-in and boot screens from presentation data."""
        if frame.screen == "signin":
            self.draw_signin(frame.signin)
            return
        if frame.screen != "boot":
            return

        if self._signin:
            self.undraw_signin(frame.signin)
        self.draw_footer(frame.footer, self.fullscreen_window)
        self.create_startup()
        popup_parent = self._startup if frame.popup_target == "boot" else self.fullscreen_window
        if frame.popup_kind == "lock":
            self.draw_lock(frame.lock_code, popup_parent, frame.entered_code)
        elif frame.popup_kind == "msg":
            if self._passcodebox and not frame.locked:
                self.destroy_lock()
            self.draw_messagebox(frame.popup_text, frame.popup_color, popup_parent)
        elif not frame.locked:
            if not self._startup_logo_drawn:
                self.draw_startup_logo(frame.logo)
                self._startup_logo_drawn = True
            self.draw_startup_progressbar(frame.logo, frame.progress)
            if frame.progress >= 100:
                self.clean_up_startup_animation()

    @staticmethod
    def _center_position(container_height, container_width, content_height, content_width):
        return (
            container_height // 2 - content_height // 2,
            container_width // 2 - content_width // 2,
        )

    @staticmethod
    def _image_size(image):
        return len(image), max(len(line) for line in image)

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
            text = text[:max(0, self._footer.width - 2)]
            x = max(0, self._footer.width // 2 - len(text) // 2)
            try:
                self._footer.write_simple(text, y=0, x=x, color=Colors.DEFAULT)
            except curses.error:
                pass
            self._footer.refresh()

    def draw_lock(self, code, parent_window, entered_code):
        if self._passcodebox is None:
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

        logo_height, logo_width = self._image_size(logo)
        start_y, start_x = self._center_position(
            self._screen_height, self._screen_width, logo_height + 2, logo_width
        )

        for i, line in enumerate(logo):
            self._startup.write_simple(line, y=start_y + i, x=start_x, color=Colors.DEFAULT, bold=True)
            self._startup.refresh()
            time.sleep(0.35)

    def draw_startup_progressbar(self, logo, progress):
        if not self._startup:
            return

        logo_height, logo_width = self._image_size(logo)
        bar_length = logo_width
        start_y, _ = self._center_position(
            self._startup.height, self._startup.width, logo_height + 2, logo_width
        )
        bar_y = start_y + logo_height + 1
        _, bar_x = self._center_position(
            self._startup.height, self._startup.width, logo_height + 2, logo_width
        )

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
            self._startup_logo_drawn = False

    def draw_signin(self, image=""):
        image_height, image_width = self._image_size(image)
        start_y, start_x = self._center_position(
            self._screen_height, self._screen_width, image_height, image_width
        )

        if self._signin is None:
            self._signin = Window(self._screen_height, self._screen_width, 0, 0)
            self._signin.background = Colors.DEFAULT

        for i, line in enumerate(image):
            self._signin.write_simple(line, y=start_y + i, x=start_x, color=Colors.SELECTED, bold=True)
            self._signin.refresh()
            time.sleep(0.1)

    def undraw_signin(self, image=""):
        if self._signin:
            image_height, image_width = self._image_size(image)
            start_y, start_x = self._center_position(
                self._signin.height, self._signin.width, image_height, image_width
            )

            for i, line in enumerate(image):
                self._signin.write_simple(" " * len(line), y=start_y + i, x=start_x, color=Colors.DEFAULT, bold=True)
                self._signin.refresh()
                time.sleep(0.1)

            del self._signin
            self._signin = None


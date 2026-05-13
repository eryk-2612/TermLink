import curses
import time
from unittest import skip

from core import Colors, TokensDE, Others

class PasscodeBox:
    def __init__(self, parent_window, code_length=5, entered_code="", title=TokensDE.PASSCODE, color=Colors.DEFAULT):
        self.parent_window = parent_window
        self.code_length = code_length
        self.entered_code = entered_code
        self.title = title
        self.color = color

        self.box_height = 4
        self.box_width = code_length * 2 + 3

        self.parent_height = self.parent_window.height
        self.parent_width = self.parent_window.width

        # relativ im Parent zentriert
        self.y = self.parent_height // 2 - self.box_height // 2
        self.x = self.parent_width // 2 - self.box_width // 2

        # Subwindow im Parent
        self.win = self.parent_window.win.derwin(self.box_height,self.box_width,self.y,self.x)
        self.title_win = self.win.derwin(1,self.box_width,0,0)
        self.input_win = self.win.derwin(self.box_height - 1, self.box_width, 1, 0)

    def draw(self):
        title = self.title.upper()
        title_x = (self.box_width - len(title)) // 2
        self.title_win.addstr( 0, title_x, title, curses.color_pair(Colors.DEFAULT) | curses.A_BOLD)
        self.type(self.entered_code)
        self.input_win.refresh()
        self.input_win.box()

        self.win.bkgd(' ', curses.color_pair(self.color))
        self.title_win.bkgd(' ', curses.color_pair(self.color))
        self.input_win.bkgd(' ', curses.color_pair(self.color))

        self.refresh()

    def refresh(self):
        self.win.refresh()
        self.title_win.refresh()
        self.input_win.refresh()

    def write(self, text, y=1, x=2, color=Colors.DEFAULT):
        self.input_win.addstr(y, x, text, curses.color_pair(color) | curses.A_BOLD)
        self.input_win.refresh()

    def type(self, entered_code):
        start_x = 2
        for i in range(self.code_length):
            x_pos = start_x + i * 2
            char = entered_code[i] if i < len(entered_code) else Others.CODE_PLACEHOLDER
            self.write(char, y=1, x=x_pos, color=Colors.DEFAULT)
        self.win.refresh()

class Messagebox:
    def __init__(self, parent_window, text, color=Colors.DEFAULT, duration=1.5):
        self.win = None
        self._parent_window = parent_window
        self.text = text
        self.duration = duration
        self.expires_at = time.time() + self.duration
        self.drawn = False
        self.color = color
        self._skip = False

        self.messagebox_height = 3
        self.messagebox_width = len(text) + 4

        self.parent_height = self.parent_window.height
        self.parent_width = self.parent_window.width

        self.y = self.parent_height // 2 - self.messagebox_height // 2
        self.x = self.parent_width // 2 - self.messagebox_width // 2

    @property
    def parent_window(self):
        return self._parent_window

    @property
    def visible(self):
        if self._skip:
            return False
        else:
            return time.time() < self.expires_at

    def skip(self):
        self._skip = True

    def draw(self):
        if self.drawn:
            return
        self.parent_window.reload()
        self.win = self.parent_window.win.derwin(self.messagebox_height,self.messagebox_width,self.y,self.x)
        self.win.bkgd(' ', curses.color_pair(self.color))
        self.win.box()
        self.write(self.text,y=1,x=2,delay=0.02,color=self.color,bold=True)
        self.win.refresh()
        self.drawn = True

    def write(self, text, y=1, x=2, delay=0.0, color=Colors.DEFAULT, bold=False):
        curses.flushinp()
        for char in text:
            if bold:
                self.win.addstr(y,x,char,curses.color_pair(color) | curses.A_BOLD)
            else:
                self.win.addstr(y,x,char,curses.color_pair(color))
            x += 1
            self.win.refresh()
            time.sleep(delay)

    def destroy(self):
        if self.win:
            self.win.clear()
            self.win.refresh()
            self.parent_window.reload()
            self.win = None
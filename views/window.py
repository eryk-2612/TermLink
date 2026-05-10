from unittest.mock import DEFAULT

from core import Colors, Others
import curses
import time
import textwrap

class Window:
    def __init__(self, height, width, begin_y, begin_x, timeout=Others.TIMEOUT, wid=None, parent_window=None):
        self.wid = wid
        self._background = Colors.DEFAULT
        self.boxed = False
        self._log = []
        self._start_x = begin_x
        self._start_y = begin_y

        if parent_window is None:
            self.win = curses.newwin(height, width, begin_y, begin_x)
        else:
            self.win = parent_window.win.derwin(height, width, begin_y, begin_x)

        self.win.timeout(timeout)
        self.win.keypad(True)
        self._win_height, self._win_width = self.win.getmaxyx()

    def refresh(self):  # Fenster aktualisieren
        self.win.refresh()

    def clear(self):
        self.win.clear()

    def reload(self):
        self.clear()
        if self.boxed:
            self.draw_box()
        self.refresh()

    def empty(self, text_length):
        # this code clears the box from old texts but keeps desired text intact - should work with line breaking text

        if self.boxed:
            padding = 1
        else:
            padding = 0

        x = padding
        y = padding

        space_width = self.width - padding * 2
        space_height = self.height  - padding * 2

        length = text_length

        if length < space_width:
            x = padding * 2 + length

        for i in range(space_height):
            if length > space_width:
                length -= space_width
                continue
            self.win.hline(i + y, x, ' ', space_width - length - padding)
            x = padding

    @property
    def log(self):
        return self._log

    @log.setter
    def log(self,value):
        self._log = value

    @property
    def width(self):
        return self._win_width

    @property
    def height(self):
        return self._win_height

    @property
    def start_x(self):
        return self.win.getbegyx()[1]

    @property
    def start_y(self):
        return self.win.getbegyx()[0]

    @width.setter
    def width(self, value):
        self._win_width = value

    @height.setter
    def height(self, value):
        self._win_height = value

    @start_x.setter
    def start_x(self, value):
        self._start_x = value

    @start_y.setter
    def start_y(self, value):
        self._start_y = value

    def draw_box(self):
        self.win.box()
        self.boxed = True

    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, color):
        self._background = color
        self.win.bkgd(' ', curses.color_pair(self.background))

    def move(self, y, x):
        self.win.mvwin(y, x)

    def resize(self, h, w):
        self.win.resize(h, w)

    def write_animate(self, text, y=1, x=2, delay=0.0, color=Colors.DEFAULT, bold=False):
        curses.flushinp()

        max_width = self.width - x - 1  # Platz bis zum Rand

        if len(text) > max_width:
            if max_width > 3:
                text = text[:max_width - 3] + "..."
            else:
                text = text[:max_width]  # falls extrem wenig Platz

        for char in text:
            if bold:
                self.win.addstr(y, x, char, curses.color_pair(color) | curses.A_BOLD)
            else:
                self.win.addstr(y, x, char, curses.color_pair(color))
            x += 1
            self.refresh()
            time.sleep(delay)

    def write_simple(self, text, y=1, x=2, color=Colors.DEFAULT, bold=False):
        if bold:
            self.win.addstr(y, x, text, curses.color_pair(color) | curses.A_BOLD)
        else:
            self.win.addstr(y, x, text, curses.color_pair(color))
        self.refresh()

    def write_new_line(self, text, delay=0.0, color=Colors.DEFAULT, bold=False):
        if text == "":
            self.log.append("")  # Log erweitern
            self.write_animate("", y=len(self.log))  # in der letzten Zeile schreiben
        else:
            wrapped = textwrap.wrap(text, self.width - 4)
            self.log.extend(wrapped)
            last_line = len(self.log) - len(wrapped) # bestimmt die letzte zeile des logs
            for i, line in enumerate(self.log):
                if i >= last_line:
                    self.write_animate(line, i + 1, delay=delay, color=color, bold=bold)  # animieren
                else:
                    self.write_animate(line, i + 1, delay=0, color=color, bold=bold)  # nicht animieren

    def render_log(self, offset=0):
        if self.boxed:
            self.draw_box()

        visible_lines = self.height - 2
        start = offset
        end = offset + visible_lines

        for i, line in enumerate(self.log[start:end]):
            # Leere Zeile vorher überschreiben, um Reste zu löschen
            self.win.addstr(i + 1, 2, " " * (self.width - 4))
            self.write_simple(line, y=i + 1, x=2)

        self.refresh()

    def dump_log(self):
        self.log = []
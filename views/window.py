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

    def resize(self, height, width):
        self.win.resize(height, width)
        self.height, self.width = height, width

    def write_animate(self, text, y=1, x=2, delay=0.0, color=Colors.DEFAULT, bold=False):
        curses.flushinp()

        max_width = self.width - x - 1

        if len(text) > max_width:
            if max_width > 4:
                text = text[:max_width - 4] + "..."
            else:
                text = text[:max_width]

        for char in text:
            if bold:
                self.win.addstr(y, x, char, curses.color_pair(color) | curses.A_BOLD)
            else:
                self.win.addstr(y, x, char, curses.color_pair(color))
            x += 1
            self.refresh()
            time.sleep(delay)

    def write_simple(self, text, y=1, x=2, color=Colors.DEFAULT, bold=False):
        self.win.addstr(y, x, text, curses.color_pair(color) | (curses.A_BOLD if bold else 0))
        self.refresh()

    def write_new_line(self, text, delay=0.0, color=Colors.DEFAULT, bold=False):
        lines = text.split("\n")

        for part in lines:
            wrapped = textwrap.wrap(part, self.width - 4)

            if not wrapped:
                self.log.append("")
                self.write_animate("", y=len(self.log), delay=delay, color=color, bold=bold)
            else:
                start_index = len(self.log)
                self.log.extend(wrapped)

                for i, line in enumerate(wrapped):
                    self.write_animate(line, start_index + i + 1, delay=delay ,color=color, bold=bold)

    def log_lines(self, lines):
        if lines:
            for line in lines:
                split_lines = line.split('\n')
                for subline in split_lines:
                    wrapped = textwrap.wrap(subline, self.width - 2)
                    self.log.extend(wrapped if wrapped else [''])

    def render_log(self, offset=0):
        visible_lines = self.height
        start = offset
        end = offset + visible_lines

        for i, line in enumerate(self.log[start:end]):
            self.win.addstr(i, 1, " " * (self.width -2))
            self.write_simple(line, y=i, x=1)

        self.refresh()

    def dump_log(self):
        self.log = []

    def get_visible_log_lines(self):
        return self.height

    def get_max_scroll_offset(self):
        visible_lines = self.get_visible_log_lines()
        return max(0, len(self.log) - visible_lines)

    def refresh(self):
        self.win.refresh()

    def clear(self):
        self.win.clear()

    def reload(self):
        self.clear()
        if self.boxed:
            self.draw_box()
        self.refresh()

    def empty(self, text_length=0):
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

            try:
                self.win.hline(i + y, x, ' ', space_width - length - padding)
            except curses.error:
                pass # I know this is silly but it works
            x = padding
        self.refresh()

    def clear_line(self, y, x, width):
        try:
            self.win.addstr(y, x, " " * width)
        except curses.error:
            pass
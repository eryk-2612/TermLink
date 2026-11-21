import curses
import time
from core import Colors, Tokens, Others
from .window import Window

class Popup:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.win = None
        self._underlay = None

    def undraw(self):
        if self.win:
            self.clear()
            self.win = None

    def clear(self):
        if self._underlay is not None:
            try:
                self._underlay.overwrite(self.win)
            except curses.error:
                self.win.clear()
        else:
            self.win.clear()
        self.win.refresh()
        self._underlay = None

    def capture_underlay(self):
        if not self.win or self._underlay is not None:
            return
        height, width = self.win.getmaxyx()
        parent_y, parent_x = self.parent_window.win.getbegyx()
        self._underlay = curses.newwin(
            height, width, parent_y + self.y, parent_x + self.x
        )
        self.win.overwrite(self._underlay)

    @staticmethod
    def centered_position(parent_window, height, width):
        """Use the parent window's dimensions consistently for popup placement."""
        return (
            parent_window.height // 2 - height // 2,
            parent_window.width // 2 - width // 2,
        )

class PasscodeBox(Popup):
    def __init__(self, parent_window, code_length=5, title=Tokens.PASSCODE, color=Colors.DEFAULT):
        super().__init__(parent_window)

        self.code_length = code_length
        self.title = title
        self.color = color
        self._painted = False
        self._last_entered_code = None

        self.box_height = 4
        self.box_width = max((code_length * 2 + 3), len(self.title) + 2)

        # Center the visible slots, not the nominal ``2 * length`` stride.
        # Matching the box width parity to the slot width gives equal margins.
        display_width = max(1, code_length * 2 - 1)
        max_width = max(1, self.parent_window.width - 2)
        self.box_width = min(self.box_width, max_width)
        if (self.box_width - display_width) % 2:
            if self.box_width < max_width:
                self.box_width += 1
            elif self.box_width > display_width + 2:
                self.box_width -= 1

        self.y, self.x = self.centered_position(
            self.parent_window, self.box_height, self.box_width
        )

        self.win = self.parent_window.win.derwin(self.box_height, self.box_width, self.y, self.x)
        self.win.timeout(Others.TIMEOUT)
        self.win.keypad(True)
        self.title_win = self.win.derwin(1, self.box_width, 0, 0)
        self.input_win = self.win.derwin(self.box_height - 1, self.box_width, 1, 0)

    def draw(self, entered_code):
        self.capture_underlay()
        if not self._painted:
            self.win.bkgd(' ', curses.color_pair(self.color))
            self.title_win.bkgd(' ', curses.color_pair(self.color))
            self.input_win.bkgd(' ', curses.color_pair(self.color))
            self.win.erase()
            title = self.title.upper()
            title = title[:max(0, self.box_width - 2)]
            title_x = max(0, (self.box_width - len(title)) // 2)
            try:
                self.title_win.addstr(
                    0, title_x, title, Window.text_attributes(Colors.DEFAULT, bold=True)
                )
            except curses.error:
                pass
            self.input_win.box()
            self._painted = True
            self.title_win.refresh()

        if entered_code != self._last_entered_code:
            self.type(entered_code)
            self._last_entered_code = entered_code
            self.input_win.refresh()

    def refresh(self):
        self.win.refresh()
        self.title_win.refresh()
        self.input_win.refresh()

    def write(self, text, y=1, x=2, color=Colors.DEFAULT):
        try:
            self.input_win.addstr(y, x, text, Window.text_attributes(color, bold=True))
        except curses.error:
            pass

    def type(self, entered_code):
        display_slots = min(self.code_length, max(0, (self.box_width - 1) // 2))
        display_width = max(0, display_slots * 2 - 1)
        inner_width = max(0, self.box_width - 2)
        start_x = 1 + max(0, (inner_width - display_width) // 2)
        for i in range(display_slots):
            x_pos = start_x + i * 2
            char = entered_code[i] if i < len(entered_code) else Others.CODE_PLACEHOLDER
            self.write(char, y=1, x=x_pos, color=Colors.DEFAULT)

class Messagebox(Popup):
    def __init__(self, parent_window, text, color=Colors.DEFAULT):
        super().__init__(parent_window)

        self.text = text
        self._drawn = False
        self.color = color
        lines = text.split("\n")

        self.messagebox_height = len(lines) + 2
        self.messagebox_width = max(len(line) for line in lines) + 4
        self._parent_underlay = None

        self.y, self.x = self.centered_position(
            self.parent_window, self.messagebox_height, self.messagebox_width
        )

    @property
    def drawn(self):
        return self._drawn

    def draw(self):
        if self.drawn:
            return
        self.win = self.parent_window.win.derwin(self.messagebox_height,self.messagebox_width,self.y,self.x)
        self.win.timeout(Others.TIMEOUT)
        self.win.keypad(True)

        parent_y, parent_x = self.parent_window.win.getbegyx()
        self._parent_underlay = curses.newwin(
            self.parent_window.height, self.parent_window.width, parent_y, parent_x
        )
        self.parent_window.win.overwrite(self._parent_underlay)
        self.parent_window.background = Colors.DEFAULT
        self.parent_window.win.erase()
        if self.parent_window.boxed:
            self.parent_window.draw_box()
        self.parent_window.refresh()

        self.win.bkgd(' ', curses.color_pair(self.color))
        self.win.erase()
        self.win.box()
        self.write(self.text,y=1,x=2,delay=0.02,color=self.color,bold=True)
        self.win.refresh()
        self._drawn = True

    def clear(self):
        if self._parent_underlay is None:
            return super().clear()
        self._parent_underlay.overwrite(self.parent_window.win)
        self.parent_window.refresh()
        self._parent_underlay = None

    def write(self,text, y=None, x=None, delay=0.0, color=Colors.DEFAULT, bold=False, centered=True):
        curses.flushinp()

        lines = text.split("\n")

        if y is None:
            y = (self.messagebox_height // 2) - (len(lines) // 2)

        attr = Window.text_attributes(color, bold)

        for line_index, line in enumerate(lines):

            current_y = y + line_index

            if centered:
                usable_width = self.messagebox_width - 2
                current_x = 1 + ((usable_width - len(line)) // 2)
            else:
                current_x = x if x is not None else 0

            for char in line:
                try:
                    self.win.addstr(current_y, current_x, char, attr)
                except curses.error:
                    pass

                current_x += 1

                if delay > 0:
                    self.win.refresh()
                    time.sleep(delay)

        self.win.refresh()

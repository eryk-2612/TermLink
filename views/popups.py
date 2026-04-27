import curses
import time
from core import Colors, TokensDE

class PasscodeBox:
    def __init__(self, parent_window, code_length=5, title=TokensDE.PASSCODE, color=Colors.DEFAULT):
        self.parent_window = parent_window
        self.code_length = code_length
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
        self.title_win.addstr(0, 1, self.title.upper(), curses.color_pair(Colors.DEFAULT) | curses.A_BOLD)
        self.type("")
        self.input_win.box()

        self.win.bkgd(' ', curses.color_pair(self.color))
        self.title_win.bkgd(' ', curses.color_pair(self.color))
        self.input_win.bkgd(' ', curses.color_pair(self.color))

        self.refresh()

    def refresh(self):
        self.win.refresh()
        self.title_win.refresh()
        self.input_win.refresh()

    def write(self, text, y=1, x=2, color=Colors.TEXT):
        self.input_win.addstr(y, x, text, curses.color_pair(color) | curses.A_BOLD)
        self.input_win.refresh()

    def type(self, entered_code):
        start_x = 2

        for i in range(self.code_length):
            x_pos = start_x + i * 2
            char = entered_code[i] if i < len(entered_code) else "_"
            self.write(char, y=1, x=x_pos, color=Colors.TEXT)

        self.win.refresh()

class Messagebox:
    def __init__(self, parent_window, text, color=Colors.DEFAULT, duration=1):
        self.parent_window = parent_window
        self.text = text
        self.duration = duration
        self.color = color

        self.messagebox_height = 3
        self.messagebox_width = len(text) + 4

        self.parent_height = self.parent_window.height
        self.parent_width = self.parent_window.width

        # relativ im Parent zentriert
        self.y = self.parent_height // 2 - self.messagebox_height // 2
        self.x = self.parent_width // 2 - self.messagebox_width // 2

        # im Parent erzeugen
        self.win = self.parent_window.win.derwin(self.messagebox_height,self.messagebox_width,self.y,self.x)

    def draw(self):
        self.win.bkgd(' ', curses.color_pair(self.color))
        self.win.box()
        self.write(self.text,y=1,x=2,delay=0.02,color=self.color,bold=True)
        self.win.refresh()
        time.sleep(self.duration)

    def write(self, text, y=1, x=2, delay=0.0, color=Colors.TEXT, bold=False):
        curses.flushinp()
        for char in text:
            if bold:
                self.win.addstr(y,x,char,curses.color_pair(color) | curses.A_BOLD)
            else:
                self.win.addstr(y,x,char,curses.color_pair(color))
            x += 1
            self.win.refresh()
            time.sleep(delay)
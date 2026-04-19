import curses
from core import Colors, TokensDE

class PasscodeBox:
    def __init__(self, parent_window, code_length=5, title=TokensDE.PASSCODE, color=Colors.DEFAULT):
        self.parent_window = parent_window
        self.code_length = code_length
        self.title = title
        self.color = color

        self.box_height = 3
        self.box_width = code_length * 2 + 3

        self.parent_height = self.parent_window.height
        self.parent_width = self.parent_window.width

        # relativ im Parent zentriert
        self.y = self.parent_height // 2 - self.box_height // 2
        self.x = self.parent_width // 2 - self.box_width // 2

        # echtes Subwindow im Parent
        self.win = self.parent_window.win.derwin(self.box_height,self.box_width,self.y,self.x)

    @property
    def width(self):
        return self.box_width

    @property
    def height(self):
        return self.box_height

    def refresh(self):
        self.win.refresh()

    def draw_box(self):
        self.win.box()

    def write(self, text, y=1, x=2, color=Colors.TEXT, bold=False):
        if bold:self.win.addstr(y,x,text,curses.color_pair(color) | curses.A_BOLD)
        else:
            self.win.addstr(y,x,text,curses.color_pair(color))

    def draw(self):
        # Titel im Parent
        title_y = self.y - 1
        title_x = self.parent_width // 2 - len(self.title) // 2

        self.parent_window.write_simple(self.title.upper(),y=title_y,x=title_x,color=Colors.DEFAULT,bold=True)

        self.win.bkgd(' ', curses.color_pair(self.color))
        self.draw_box()
        self.refresh()

    def get_passcode(self):
        entered_code = []
        trigger = ""

        while True:
            start_x = 1 + (self.box_width - self.code_length * 2) // 2

            for i in range(self.code_length):
                x_pos = start_x + i * 2
                char = entered_code[i] if i < len(entered_code) else "_"

                self.write(char,y=1,x=x_pos,color=Colors.TEXT,bold=True)

            self.refresh()

            key = self.win.getch()

            if key in range(ord('0'), ord('9') + 1) and len(entered_code) < self.code_length:
                entered_code.append(chr(key))

            elif key in [curses.KEY_BACKSPACE, 127, 8]:
                if entered_code:
                    entered_code.pop()

            elif key in [10, 13]:
                if len(entered_code) == self.code_length:
                    trigger = "enter"
                    break

            elif key in [curses.KEY_UP, 27]:
                trigger = "esc"
                break

        return ''.join(entered_code), trigger

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

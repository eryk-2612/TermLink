from views.terminal_view import TerminalView
from .window import Window
from core import Colors, Others, Tokens

class ChatView(TerminalView):
    def __init__(self, stdscr):
        super().__init__(stdscr)

        self._header = None
        self._inputwin = None
        self._outputwin = None
        self._chat = None

    @property
    def chat_window(self):
        if not self._chat:
            self._chat = Window(self._screen_height, self._screen_width, 0, 0)
        return self._chat

    def draw_header(self, title=""):
        if not self._header:
            self._header = Window(1, self._screen_width, 0, 0, parent_window=self._chat)
            self._header.background = Colors.SELECTED
            self._header.write_simple(title.upper(), y=0, x=1, color=Colors.SELECTED, bold=True)
            self._header.refresh()

    def draw_output_window(self, text=""):
        if not self._outputwin:
            height = self._screen_height - self._header.height - self._footer.height - 3
            width = self._screen_width - Others.SCREEN_PADDING
            y = self._header.height
            x = 0
            self._outputwin = Window(height, width, y, x, parent_window=self._chat)
            self._outputwin.draw_box()
            self._outputwin.refresh()

        if not text == "":
            try:
                self._outputwin.write_new_line(text, 0.05, bold=True)
            except:
                self._outputwin.dump_log()
                self._outputwin.empty()
                self._outputwin.write_new_line(text, 0.05, bold=True)

    def draw_input_window(self, input=""):
        if not self._inputwin  and self._outputwin:
            height = 3
            width = self._screen_width - Others.SCREEN_PADDING
            y = self._outputwin.height + Others.SCREEN_PADDING
            x = 0
            self._inputwin = Window(height, width, y, x, parent_window=self._chat)
            self._inputwin.refresh()

        cursor = "> "
        self._inputwin.win.move(1, 1)
        self._inputwin.win.clrtoeol()
        self._inputwin.draw_box()
        max_len = self._inputwin.width - len(cursor) - Others.BORDER_PADDING * 2
        if len(input) >= max_len:
            input = input[-max_len:]
        self._inputwin.write_simple(cursor + input, color=Colors.DEFAULT)

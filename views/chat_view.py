from views.terminal_view import TerminalView
from .window import Window
from core import Colors, Others

class ChatView(TerminalView):
    def __init__(self, stdscr):
        super().__init__(stdscr)

        self._header = None
        self._inputwin = None
        self._outputwin = None
        self._chat = None
        self._outputwin_inner = None
        self._scrollbar = None


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

    def draw_output_window(self):
        if not self._outputwin:
            height = self._screen_height - self._header.height - self._footer.height - 3
            width = self._screen_width - Others.SCREEN_PADDING
            y = self._header.height
            x = 0
            self._outputwin = Window(height, width, y, x, parent_window=self._chat)
            self._outputwin.draw_box()
            self._outputwin.refresh()

    def display_text(self, lines, scroll_offset):
        if not self._outputwin:
            return

        if not self._outputwin_inner:
            self._outputwin_inner = Window(self._outputwin.height - 2, self._outputwin.width - 3, 1, 1, parent_window=self._outputwin)

        if self._outputwin_inner:
            self._outputwin_inner.dump_log()
            self._outputwin_inner.log_lines(lines)
            self._outputwin_inner.render_log(scroll_offset)

        self._scrollbar = self.draw_scrollbar(self._outputwin, self._scrollbar, self._outputwin.height - 2, self.get_chat_max_scroll(), 0, scroll_offset, 1, self._outputwin.width - 2)

    def clear_outputwin(self):
        if not self._outputwin:
            return
        else:
            self._outputwin.empty()

        if not self._outputwin_inner:
            return
        else:
            self._outputwin_inner.empty()

        if not self._scrollbar:
            return
        else:
            self._scrollbar.empty()

        self._outputwin.reload()

    def get_chat_max_scroll(self):
        if not self._outputwin_inner:
            return 0
        return self._outputwin_inner.get_max_scroll_offset()

    def draw_scrollbar(self, parent_win, scrollbar_win, height, total, visible_count, scroll_offset, y, x):
        if not scrollbar_win:
            scrollbar_win = Window(height, 1, y, x, parent_window=parent_win)

        up_y = 1
        down_y = max(1, height - 2)

        can_scroll_up = scroll_offset > 0
        can_scroll_down = scroll_offset + visible_count < total

        scroll_needed = total > visible_count

        arrow_up = "△"
        arrow_down = "▽"

        if can_scroll_up:
            arrow_up = "▲"

        if can_scroll_down:
            arrow_down = "▼"

        if not scroll_needed:
            arrow_up = " "
            arrow_down = " "

        if up_y == down_y:
            if can_scroll_up:
                scrollbar_win.write_simple(arrow_up, up_y, 0)
            elif can_scroll_down:
                scrollbar_win.write_simple(arrow_down, down_y, 0)
        else:
            scrollbar_win.write_simple(arrow_up, up_y, 0)
            scrollbar_win.write_simple(arrow_down, down_y, 0)
        return scrollbar_win

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

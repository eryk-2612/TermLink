import curses
from core import *
from controllers import *
from models import *
from states.state import *
from views import *

def init_colors():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK) # Default
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE) # Selected

def init_menu(height, width, terminals, stdscr):
    current_idx = 0
    drawn_idx = None
    menu = terminals + [Tokens.LOAD_FROM_DISK, Tokens.LEAVE]

    def draw_item(idx, selected):
        item = menu[idx]
        if item == Tokens.LEAVE or item == Tokens.LOAD_FROM_DISK:
            text = item.upper()
        else:
            text = item.model.name.upper()

        x = width // 2 - len(text) // 2
        y = height // 2 - len(menu) // 2 + idx
        color = Colors.SELECTED if selected else Colors.DEFAULT
        attributes = curses.color_pair(color) | (curses.A_BOLD if selected else 0)
        try:
            stdscr.addstr(y, x, text, attributes)
        except curses.error:
            pass

    while True:
        if drawn_idx is None:
            stdscr.erase()
            for idx in range(len(menu)):
                draw_item(idx, idx == current_idx)
            stdscr.refresh()
            drawn_idx = current_idx
        elif drawn_idx != current_idx:
            draw_item(drawn_idx, False)
            draw_item(current_idx, True)
            stdscr.refresh()
            drawn_idx = current_idx

        key = stdscr.getch()
        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(menu)
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(menu)
        elif key in [10, 13, curses.KEY_ENTER]:
            selected = menu[current_idx]
            stdscr.erase()
            stdscr.refresh()
            if selected == Tokens.LEAVE:
                return None
            return selected

def create_controller(stdscr, model, disk_loaded=False):
    if isinstance(model, ChatModel):
        return ChatController(stdscr, model, ChatView(stdscr), ChatState())
    if isinstance(model, ExplorerModel):
        return ExplorerController(stdscr, model, ExplorerView(stdscr), ExplorerState(), disk_loaded=disk_loaded)
    return TerminalController(stdscr, model, TerminalView(stdscr), TerminalState())

def main(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    stdscr.timeout(300)
    init_colors()

    loader = JsonLoader(Others.DATA_PATH)
    terminals = loader.load_all_terminals()

    while True:
        controller_list = [create_controller(stdscr, model) for model in terminals]

        height, width = stdscr.getmaxyx()
        selected_controller = init_menu(height, width, controller_list, stdscr)

        if selected_controller == Tokens.LOAD_FROM_DISK:
            loaded_model = DiskTerminalController(stdscr).run()
            if loaded_model:
                stdscr.erase()
                stdscr.refresh()
                create_controller(stdscr, loaded_model, disk_loaded=True).run()
        elif selected_controller:
            stdscr.refresh()
            selected_controller.run()
        else:
            break

curses.wrapper(main)

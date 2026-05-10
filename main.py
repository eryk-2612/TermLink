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

def init_menu(height, width, terminals):
    win = Window(height, width, 0, 0)
    current_idx = 0
    menu = terminals + [TokensDE.LEAVE]
    
    while True:
        # Alle Einträge zentriert zeichnen
        for idx, item in enumerate(menu):
            if item == TokensDE.LEAVE:
                text = TokensDE.LEAVE.upper()
            else:
                text = item.model.name.upper()

            x = width // 2 - len(text) // 2
            y = height // 2 - len(menu) // 2 + idx

            if idx == current_idx:
                win.write_simple(text, y, x, Colors.SELECTED, True)
            else:
                win.write_simple(text, y, x, Colors.DEFAULT, False)

        # Eingabe abfragen
        key = win.win.getch()
        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(menu)
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(menu)
        elif key in [10, 13, curses.KEY_ENTER]:
            selected = menu[current_idx]
            if selected == TokensDE.LEAVE:
                return None
            win.reload()
            del win
            return selected

def main(stdscr):
    curses.curs_set(0)  # Versteckt den curser
    stdscr.keypad(True) # Aktiviert das numpad
    stdscr.timeout(300) # nach 300ms input skippen
    init_colors()       # Init Farben

    loader = JsonLoader()
    terminals = loader.load_all_terminals()

    controller_list = []
    for model in terminals:
        if isinstance(model, ChatModel):
            view = ChatView(stdscr)
            state = ChatState()
            controller_list.append(ChatController(stdscr, model, view, state))
        elif isinstance(model, ExplorerModel):
            view = ExplorerView(stdscr)
            state = ExplorerState()
            controller_list.append(ExplorerController(stdscr, model, view, state))
        else:
            view = TerminalView(stdscr)
            state = TerminalState()
            controller_list.append(TerminalController(stdscr, model, view, state))

    while True:
        height, width = stdscr.getmaxyx()
        selected_controller = init_menu(height, width, controller_list)

        if selected_controller:
            stdscr.refresh()
            selected_controller.run()
        else:
            break

curses.wrapper(main)
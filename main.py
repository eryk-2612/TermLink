import curses
from core import *
from core.color_config import load_color_pairs
from controllers import *
from models import *
from states.state import *
from views import *
from controllers.menu_controller import MenuController
from controllers.menu_controller import MenuController

def init_colors():
    curses.start_color()
    pairs = load_color_pairs()
    curses.init_pair(Colors.DEFAULT, *pairs["default"])
    curses.init_pair(Colors.SELECTED, *pairs["selected"])

def init_menu(height, width, terminals, stdscr):
    """Show the main menu through its dedicated controller and view."""
    # Keep application startup wiring separate from the menu interaction loop.
    return MenuController(stdscr, height, width, terminals).run()

def create_controller(stdscr, model):
    """Build the matching controller and view for a terminal model."""
    if isinstance(model, ChatModel):
        return ChatController(stdscr, model, ChatView(stdscr), ChatState())
    if isinstance(model, ExplorerModel):
        return ExplorerController(stdscr, model, ExplorerView(stdscr), ExplorerState())
    return TerminalController(stdscr, model, TerminalView(stdscr), TerminalState())

def main(stdscr):
    curses.curs_set(0)
    # Keep Escape responsive while still allowing curses to recognize key sequences.
    curses.set_escdelay(25)
    stdscr.keypad(True)
    stdscr.timeout(300)
    init_colors()
    stdscr.bkgd(" ", curses.color_pair(Colors.DEFAULT))
    stdscr.erase()
    stdscr.refresh()

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
                create_controller(stdscr, loaded_model).run()
        elif selected_controller:
            stdscr.refresh()
            selected_controller.run()
        else:
            break

curses.wrapper(main)

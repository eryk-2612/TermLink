from dataclasses import dataclass
from core import Screens, Events, Focus
from models import CategoryModel, EntryModel

@dataclass
class TerminalState:
    running: bool = True
    screen: str = Screens.SIGNIN
    event: str = Events.INIT
    focus: str = None

@dataclass
class ChatState(TerminalState):
    response: str = ""
    request: str = ""
    input_buffer: str = ""

@dataclass
class ExplorerState(TerminalState):
    selected_category: CategoryModel = None
    selected_entry: EntryModel = None
    open_category: CategoryModel = None
    open_entry: EntryModel = None
    index: int = 0
    switch_selected: int = 0
    scroll_offset = int = 0

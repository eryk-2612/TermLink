from dataclasses import dataclass
from models import CategoryModel, EntryModel

@dataclass
class MessageboxState:
    show: bool = False
    message: str = ""
    color: int = 0

@dataclass
class TerminalState:
    running: bool = None
    screen: str = None
    event: str = None
    focus: str = None
    entered_code: str = ""
    msgbox: MessageboxState = None

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

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
    boot_completed: bool = False

@dataclass
class ChatState(TerminalState):
    response: str = ""
    request: str = ""
    input_buffer: str = ""

@dataclass
class ExplorerState(TerminalState):
    selected_category: int = 0
    selected_entry: int = 0
    open_category: CategoryModel = None
    open_entry: EntryModel = None
    c_index: int = 0
    e_index: int = 0
    switch_selected: int = 0
    category_scroll_offset: int = 0
    entry_scroll_offset: int = 0

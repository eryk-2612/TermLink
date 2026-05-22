from dataclasses import dataclass, field
from models import CategoryModel, EntryModel

@dataclass
class TerminalState:
    running: bool = None
    screen: str = None
    event_queue: list = field(default_factory=list)
    focus: str = None
    active_popup: str = None
    entered_code: str = ""
    boot_completed: bool = False

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
    content_scroll_offset: int = 0

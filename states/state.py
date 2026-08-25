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
    loading_progress: int = 0
    boot_logo_drawn: bool = False

@dataclass
class ExplorerState(TerminalState):
    selected_category: int = 0
    selected_entry: int = 0
    open_category: CategoryModel = None
    open_entry: EntryModel = None
    category_index: int = 0
    entry_index: int = 0
    switch_selected: int = 0
    category_scroll_offset: int = 0
    entry_scroll_offset: int = 0
    content_scroll_offset: int = 0
    floppy_drive_found: bool = False
    floppy_init: bool = False
    floppy_data_loaded: bool = False
    notification: str = ""
    show_notification: bool = False
    notification_timeout: int = None
    force_header: bool = False

@dataclass
class ChatState(TerminalState):
    _input_text: str = ""
    output_text: str = ""
    _request: str = ""
    ai_loaded: bool = False
    chat_scroll_offset: int = 0

    @property
    def input_text(self):
        return self._input_text

    @input_text.setter
    def input_text(self, value):
        self._input_text = value

    def clear_input_text(self):
        self.request = self._input_text
        self._input_text = ""

    @property
    def request(self):
        buffer = self._request
        self._request = ""
        return buffer

    @request.setter
    def request(self, value):
        self._request = value
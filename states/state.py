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
    category_index: int = 0
    entry_index: int = 0
    switch_selected: int = 0
    category_scroll_offset: int = 0
    entry_scroll_offset: int = 0
    content_scroll_offset: int = 0

@dataclass
class ChatState(TerminalState):
    _input_text: str = ""
    _output_text: str = ""
    _request: str = ""

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
    def output_text(self):
        buffer = self._output_text
        self._output_text = ""
        return buffer

    @output_text.setter
    def output_text(self, value):
        self._output_text = value

    @property
    def request(self):
        buffer = self._request
        self._request = ""
        return buffer

    @request.setter
    def request(self, value):
        self._request = value
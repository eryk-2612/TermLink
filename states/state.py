from dataclasses import dataclass, field
from typing import Literal
from models import CategoryModel, EntryModel

ScreenName = Literal["signin", "boot", "explorer", "chat"]
FocusName = Literal["categories", "entries", "content", "lock", "input"]
PopupKind = Literal["msg", "lock"]
EventName = Literal[
    "close_entry", "open_entry", "open_category", "close_category",
    "cancel", "signin", "quit", "request",
]


@dataclass
class PopupState:
    """Keep popup content, placement, and lifetime as one consistent value."""
    kind: PopupKind
    text: str = ""
    color: int = 1
    target: str = ""
    expires_at: float | None = None


@dataclass
class TerminalState:
    """Runtime state shared by terminal flows; presentation frames are built separately."""
    running: bool = False
    screen: ScreenName | None = None
    event_queue: list[EventName] = field(default_factory=list)
    focus: FocusName | None = None
    popup: PopupState | None = None
    entered_code: str = ""
    boot_completed: bool = False
    loading_progress: int = 0
    boot_logo_drawn: bool = False

    def show_popup(self, popup: PopupState):
        self.popup = popup

    def dismiss_popup(self):
        self.popup = None

    def popup_expired(self, now: float) -> bool:
        """Centralize timeout semantics so controllers do not inspect popup internals."""
        return self.popup is not None and self.popup.expires_at is not None and now >= self.popup.expires_at

@dataclass
class ExplorerState(TerminalState):
    """Explorer selection and domain context; viewport offsets belong to the view."""
    open_category: CategoryModel | None = None
    open_entry: EntryModel | None = None
    category_index: int = 0
    entry_index: int = 0
    switch_selected: int = 0
    floppy_drive_found: bool = False
    floppy_init: bool = False
    floppy_data_loaded: bool = False
    notification: str = ""
    show_notification: bool = False
    notification_timeout: float | None = None
    clear_content: bool = False

@dataclass
class ChatState(TerminalState):
    """Chat input and response state, independent of the output viewport."""
    _input_text: str = ""
    output_text: list[str] = field(default_factory=list)
    _request: str = ""
    ai_loaded: bool = False

    @property
    def input_text(self):
        return self._input_text

    @input_text.setter
    def input_text(self, value):
        self._input_text = value

    def submit_input(self):
        self._request = self._input_text
        self._input_text = ""

    def take_request(self):
        request = self._request
        self._request = ""
        return request

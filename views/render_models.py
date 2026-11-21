"""Immutable presentation snapshots passed from controllers to terminal views.

These models contain display-ready values rather than domain model objects, keeping
view rendering independent from controller-owned application state.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TerminalFrame:
    screen: str
    title: str = ""
    footer: str = ""
    entered_code: str = ""
    popup_text: str = ""
    popup_color: int = 1
    popup_kind: str = ""
    popup_target: str = ""
    locked: bool = False
    lock_code: str = ""
    logo: tuple = ()
    progress: int = 0
    signin: tuple = ()


@dataclass(frozen=True)
class ChatFrame:
    title: str
    footer: str
    input_text: str
    output_lines: tuple


@dataclass(frozen=True)
class DiskFrame:
    mode: str
    message: str = ""
    detail: str = ""
    filenames: tuple = ()
    selected_index: int = 0


@dataclass(frozen=True)
class EntryFrame:
    kind: str
    lines: tuple = ()
    state_labels: tuple = ()
    action_verbs: tuple = ()
    switch_selected: int = 0
    current_state: bool = False
    is_playing: bool = False
    audio_length: float = 0
    elapsed_time: float = 0


@dataclass(frozen=True)
class ExplorerFrame:
    title: str
    footer: str
    categories: tuple
    category_index: int
    entries: tuple
    entry_index: int
    focus: str
    entry: EntryFrame = None
    notification: str = ""
    popup_text: str = ""
    popup_color: int = 1
    popup_kind: str = ""
    popup_target: str = ""
    entered_code: str = ""
    locked: bool = False
    lock_code: str = ""
    clear_content: bool = False
    category_title: str = ""
    entry_title: str = ""

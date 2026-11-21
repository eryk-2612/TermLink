import curses
import json
import os

from core import FloppyManager, JsonLoader, Others, TermTypes, Tokens
from models import ChatModel, ExplorerModel
from views.disk_terminal_view import DiskTerminalView
from views.render_models import DiskFrame


class DiskTerminalController:
    """Manage disk detection, terminal discovery, and selection from removable media."""

    def __init__(self, stdscr):
        """Initialize the disk-loading flow using the shared curses screen."""
        self.stdscr = stdscr
        self.view = DiskTerminalView(stdscr)
        self.floppy = FloppyManager()
        self._mode = "waiting"
        self._terminals = []
        self._selected_index = 0
        self._read_attempts = 0
        self._max_read_attempts = 10

    def run(self):
        """Show the disk workflow and return the chosen model, or None on Escape."""
        while True:
            self._draw()
            key = self.view.read_key()

            if key == 27:
                return None
            if self._mode == "select":
                if key == curses.KEY_UP and self._selected_index > 0:
                    self._selected_index -= 1
                elif key == curses.KEY_DOWN and self._selected_index < len(self._terminals) - 1:
                    self._selected_index += 1
                elif key in (10, 13, curses.KEY_ENTER):
                    return self._terminals[self._selected_index][1]

            # While selecting, return to the insert prompt if the disk is ejected.
            if self._mode == "select" and self.floppy.update() == "removed":
                self._terminals = []
                self._selected_index = 0
                self._read_attempts = 0
                self._mode = "waiting"

            # Poll while waiting for media or for an eject after a read failure.
            if self._mode in ("waiting", "loading"):
                self._poll_floppy()
                if self._mode == "launch":
                    return self._selected_model
            elif self._mode in ("no_data", "error"):
                self._poll_for_disk_removal()

    def _draw(self):
        """Render the current disk workflow state through its view."""
        # Keep disk discovery state in the controller and pass only display values.
        message = ""
        detail = ""
        if self._mode == "waiting":
            message = Tokens.INSERT_FLOPPY
        elif self._mode == "loading":
            message = Tokens.FLOPPY_READING
        elif self._mode == "select":
            pass
        elif self._mode == "error":
            message, detail = self._error_title, self._error_message
        elif self._mode == "no_data":
            message = Tokens.FLOPPY_NO_TERMINAL
        self.view.render(DiskFrame(
            mode=self._mode,
            message=message,
            detail=detail,
            filenames=tuple(model.name for _, model in self._terminals),
            selected_index=self._selected_index,
        ))

    def _poll_floppy(self):
        """Detect inserted media, mount it, and discover supported terminal files."""
        event = self.floppy.update()
        if event == "removed":
            self._terminals = []
            self._selected_index = 0
            self._read_attempts = 0
            self._mode = "waiting"
            return
        if event not in ("inserted", "unchanged") or not self.floppy.inserted:
            return

        self._mode = "loading"
        self._draw()
        mountpoint = self.floppy.mountpoint or self.floppy.mount()
        if not mountpoint:
            self._retry_or_show_error()
            return

        try:
            self._terminals = self._read_terminals(mountpoint)
        except (OSError, json.JSONDecodeError, ValueError, TypeError):
            self._retry_or_show_error()
            return

        self._read_attempts = 0
        if not self._terminals:
            self._mode = "no_data"
            return

        if len(self._terminals) == 1:
            self._selected_model = self._terminals[0][1]
            self._mode = "launch"
            return

        self._selected_index = 0
        self._mode = "select"

    def _read_terminals(self, mountpoint):
        """Load supported complete terminals from JSON files at the mount root."""
        terminals = []
        for filename in sorted(os.listdir(mountpoint)):
            if not filename.lower().endswith(".json"):
                continue
            path = os.path.join(mountpoint, filename)
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
            terminal_data = data.get("terminal") if isinstance(data, dict) else None
            if not isinstance(terminal_data, dict):
                continue
            if terminal_data.get("type") not in (TermTypes.EXPLORER, TermTypes.CHAT):
                continue
            model = JsonLoader(Others.DATA_PATH).load_terminal(data)
            if isinstance(model, (ExplorerModel, ChatModel)):
                terminals.append((filename, model))
        return terminals

    def _show_error(self, title, detail):
        """Switch the workflow to its persistent error screen."""
        self._error_title = title
        self._error_message = detail
        self._mode = "error"

    def _retry_or_show_error(self):
        self._read_attempts += 1
        if self._read_attempts >= self._max_read_attempts:
            # Keep filesystem and parser details out of the user-facing message.
            self._show_error(Tokens.FLOPPY_READ_ERROR, "")

    def _poll_for_disk_removal(self):
        """Reset a failed read after eject so another disk can be inserted."""
        # Reset the failed attempt so another disk can be tried without leaving this screen.
        if self.floppy.update() == "removed":
            self._terminals = []
            self._selected_index = 0
            self._read_attempts = 0
            self._error_title = None
            self._error_message = ""
            self._mode = "waiting"

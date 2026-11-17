import curses
import json
import os

from core import FloppyManager, JsonLoader, Others, TermTypes, Tokens
from models import ChatModel, ExplorerModel
from views.disk_terminal_view import DiskTerminalView


class DiskTerminalController:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.view = DiskTerminalView(stdscr)
        self.floppy = FloppyManager()
        self._mode = "waiting"
        self._terminals = []
        self._selected_index = 0

    def run(self):
        while True:
            self._draw()
            key = self.stdscr.getch()

            if key == 27:
                return None
            if self._mode == "select":
                if key == curses.KEY_UP and self._selected_index > 0:
                    self._selected_index -= 1
                elif key == curses.KEY_DOWN and self._selected_index < len(self._terminals) - 1:
                    self._selected_index += 1
                elif key in (10, 13, curses.KEY_ENTER):
                    return self._terminals[self._selected_index][1]

            if self._mode == "waiting":
                self._poll_floppy()
                if self._mode == "launch":
                    return self._selected_model
            elif self._mode in ("no_data", "error"):
                self._poll_for_disk_removal()

    def _draw(self):
        if self._mode == "waiting":
            self.view.draw_message(Tokens.INSERT_FLOPPY)
        elif self._mode == "loading":
            self.view.draw_message(Tokens.FLOPPY_READING)
        elif self._mode == "select":
            self.view.draw_file_selection([model.name for _, model in self._terminals], self._selected_index)
        elif self._mode == "error":
            self.view.draw_message(self._error_title, self._error_message)
        elif self._mode == "no_data":
            self.view.draw_message(Tokens.FLOPPY_NO_TERMINAL)

    def _poll_floppy(self):
        event = self.floppy.update()
        if event not in ("inserted", "unchanged") or not self.floppy.inserted:
            return

        self._mode = "loading"
        self._draw()
        mountpoint = self.floppy.mountpoint or self.floppy.mount()
        if not mountpoint:
            self._show_error(Tokens.FLOPPY_READ_ERROR, "")
            return

        try:
            self._terminals = self._read_terminals(mountpoint)
        except (OSError, json.JSONDecodeError, ValueError, TypeError):
            self._show_error(Tokens.FLOPPY_READ_ERROR, "")
            return

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
        self._error_title = title
        self._error_message = detail[:max(0, self.view.window.width - 4)]
        self._mode = "error"

    def _poll_for_disk_removal(self):
        if self.floppy.update() == "removed":
            self._terminals = []
            self._selected_index = 0
            self._error_title = None
            self._error_message = ""
            self._mode = "waiting"

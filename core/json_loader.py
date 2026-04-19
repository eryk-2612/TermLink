import json
import os

from core import EntryTypes, TermTypes, TokensDE
from models import CategoryModel, EntryModel, ExplorerModel, ChatModel, TerminalModel

class JsonLoader:
    def __init__(self, folder="data"):
        self.folder = folder

    def load_entry(self, entry_data):
        return EntryModel(
            title=entry_data.get("title"),
            type=entry_data.get("type", EntryTypes.LOST),
            lines=entry_data.get("lines", []),
            unlock_code=entry_data.get("unlock_code"),
            default_state=entry_data.get("default_state", False),
            state_strings=entry_data.get("state_strings"),
            caption_strings=entry_data.get("caption_strings"),
            audio=entry_data.get("audio")
        )

    def load_category(self, category_data):
        entries = [self.load_entry(e) for e in category_data.get("entries", [])]
        return CategoryModel(category_data.get("title"), entries)

    def load_terminal(self, json_data):
        terminal = json_data.get("terminal", {})
        termtype = terminal.get("type")

        if termtype == TermTypes.EXPLORER:
            categories = [self.load_category(c) for c in terminal.get("categories", [])]
            # #Quit-Kategorie hinzufügen - WOANDERS HIN
            # quit_category = Category(TokensDE.LEAVE, quit=True)
            # categories.append(quit_category)
            return ExplorerModel(name=terminal.get("title", TokensDE.TERM_UNNAMED), categories=categories, unlock_code=terminal.get("unlock_code"))
        elif termtype == TermTypes.CHAT:
            return ChatModel(name=terminal.get("title", TokensDE.TERM_UNNAMED), unlock_code=terminal.get("unlock_code"))
        else:
            return TerminalModel(TokensDE.TERM_UNNAMED)

    def load_all_terminals(self):
        terminals = []

        for file in os.listdir(self.folder):
            if file.endswith(".json"):
                with open(os.path.join(self.folder, file), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    terminals.append(self.load_terminal(data))
        return terminals
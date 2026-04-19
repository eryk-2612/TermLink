import os
from .terminal_model import TerminalModel

class ChatModel(TerminalModel):
    def __init__(self, name, unlock_code=None):
        super().__init__(name, unlock_code)
        self.__api_key = os.getenv("MOTHER_API_KEY", "")

    def get_response(self, request):
        return self.simulate_response()

    @staticmethod
    def simulate_response():
        return "Oberste Priorität\nSicherstellung der Rückführung des Organismus zur Analyse. Alle anderen Überlegungen sind zweitrangig.\nBesatzung ersetztbar."
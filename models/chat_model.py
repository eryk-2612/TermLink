from .terminal_model import TerminalModel

class ChatModel(TerminalModel):
    def __init__(self, name, unlock_code=None, model=None, apikey=None, url=None, instructions=None):
        super().__init__(name, unlock_code)
        self.model = model
        self.apikey = apikey
        self.instructions = instructions
        self.url = url
        self._previous_response_id = None
        self.system_prompt = "Please. Keep your answers short. Dont use formatting like html or md and never use emojis. You may use \"\n\" where necessary. Only provide the desired output."

    @property
    def previous_response_id(self):
        return self._previous_response_id

    @previous_response_id.setter
    def previous_response_id(self, value):
        self._previous_response_id = value
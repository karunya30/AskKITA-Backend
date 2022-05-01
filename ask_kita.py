from vosk_model import VoskModel
from sphinx import Sphinx
import pyautogui
import pyperclip
import platform

class Ask_KITA:
    def __init__(self, lang, model, model_path):
        self.lang = lang
        self.model = model
        if self.model == "vosk":
            self.finalModel = VoskModel(self.lang, model_path )
        else:
            self.finalModel = Sphinx(self.lang, model_path )

    def transcribe(self):
        self.finalModel.transcribe()

    def compare2text(self):
        self.finalModel.compare2text()

    def subtitle(self, font_size):
        self.finalModel.subtitle(font_size)
    

    

  
#trial coding
import re
import time
import pytesseract
from PIL import Image
import pyautogui

from ask_kita import Ask_KITA

happy = Ask_KITA("English(US)", "vosk", r"C:\Users\karus\Documents\Final Year\FYP\Sam - Askkita and sphinx integration\Ask-kita-poc\models\vosk")

happy.subtitle(16)




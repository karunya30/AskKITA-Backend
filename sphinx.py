import speech_recognition as sr
import re
import os
import pyperclip
import platform
import time
import pytesseract
from PIL import Image
import pyautogui
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import  QCoreApplication
from LiveSubtitleWidget import LiveSubtitleWidget
import sys

class Sphinx():
    def __init__(self, lang, model_path):
        self.lang = lang #lang = en-US / ta-TA
        self.model_path = model_path#self._get_model_path()
        self.previous_length = 0


    def transcribe(self):
        try:
            if not os.path.exists(self.model_path):
                print(r"Please download a model for your language from https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/")
                print(f"and unpack into {self.model_path}.")
            r = sr.Recognizer()
            mic = sr.Microphone(device_index=1)

            while True:  # making a loop

            
                with mic as source:
                    audio = r.listen(source)

                location = self.model_path+ "\\"+ self.lang
                listened_words = r.recognize_sphinx(audio, language = location)
                listened_words_list =   listened_words.split()
                self._write(listened_words)
                #print(listened_words_list)

        except KeyboardInterrupt:
            print('\nDone -- KEYBOARDiNTERRUPT')

        except Exception as e:
            print('exception', e) 
    
    def compare2text(self):
        try:
            if not os.path.exists(self.model_path):
                print(r"Please download a model for your language from https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/")
                print(f"and unpack into {self.model_path}.")
            r = sr.Recognizer()
            mic = sr.Microphone(device_index=1)

            initial = time.perf_counter()
            words = pytesseract.image_to_string(pyautogui.screenshot(), lang="eng")
            words_clean = re.sub(r'[^\w\s]', '', words).lower()
            splitted = words.split()
            splitted_clean = words_clean.split()
            while True:  # making a loop
                
                sinceLastScreenshot = time.perf_counter()
                if (sinceLastScreenshot - initial) > 15:
                    words = pytesseract.image_to_string(pyautogui.screenshot(), lang="eng")
                    words_clean = re.sub(r'[^\w\s]', '', words).lower()
                    splitted = words.split()
                    splitted_clean = words_clean.split()
                    initial = sinceLastScreenshot

            
                with mic as source:
                    audio = r.listen(source)

                location = self.model_path+ "\\"+ self.lang
                listened_words = r.recognize_sphinx(audio, language = location)
                listened_words_list =   listened_words.split()
                self._compare(listened_words, splitted, splitted_clean)
                #print(listened_words_list)

        except KeyboardInterrupt:
            print('\nDone -- KEYBOARDiNTERRUPT')

        except Exception as e:
            print('exception', e) 

    def subtitle(self, font_size):
        app = QApplication(sys.argv)
        win = LiveSubtitleWidget(font_size)
        win.show()
        try:
            if not os.path.exists(self.model_path):
                print(r"Please download a model for your language from https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/")
                print(f"and unpack into {self.model_path}.")
            r = sr.Recognizer()
            mic = sr.Microphone(device_index=1)

            while True:  # making a loop

            
                with mic as source:
                    audio = r.listen(source)

                location = self.model_path+ "\\"+ self.lang
                listened_words = r.recognize_sphinx(audio, language = location)
                win.notificationText.setText(listened_words)
                win.adjust()
                QCoreApplication.processEvents()

        except KeyboardInterrupt:
            print('\nDone -- KEYBOARDiNTERRUPT')

        except Exception as e:
            print('exception', e) 


    def _get_model_path(self):
        full_path = os.path.realpath(__file__)
        file_dir = os.path.dirname(full_path)
        model_path = os.path.join(file_dir, 'models/sphinx')
        return model_path


    def _write(self, phrase):
        #phrase += '\n'
        pyperclip.copy(phrase)
        if platform.system() == "Darwin":
            pyautogui.hotkey("command", "v")
        else:
            pyautogui.hotkey("ctrl", "v")
        
        pyautogui.press('enter')


    def _compare(self, phrase_said, list_of_words, cleaned_list_of_words):
        print("list of words")
        print(list_of_words)
        cleaned_list_of_words = [s.replace("?","").replace(",","").replace(".","")
        .replace('"','').replace("!","").replace(":","").replace(";","") for s in list_of_words]
        print(cleaned_list_of_words)
        print("we comparing:", phrase_said)
        #words_said = phrase_said['text']
        phrase_said = phrase_said.split()
        length = len(phrase_said)
        list_of_indexes = []
        i = 0
        corresponding_indexes = [] 
        for x in range(len(phrase_said)): 
            if phrase_said[x] in cleaned_list_of_words:
                list_of_indexes.append([i for i,val in enumerate(cleaned_list_of_words) if val==phrase_said[x]])
                print(phrase_said[x],list_of_indexes[i] )
                i+=1
                corresponding_indexes.append(x)
        
        first, last = self.get_indexes(list_of_indexes, corresponding_indexes, length)
        print("positions:",first, last)

        if first!= -1:
            print("WHAT U JUST READ?")
            print(" ".join(list_of_words[first:last]))
        

    
    def get_indexes(self,list_of_indexes, corresponding_indexes, length):
        if len(list_of_indexes) == 0:
            return -1,-1
        if len(list_of_indexes) == 1:
            if len(list_of_indexes[0])==1: 
                #calculate beginning and end, and return
                #to do this, need to know index of the current one
                #otherwise assume it is not enough
                
                first = list_of_indexes[0][0] - corresponding_indexes[0]
                last = first + length
                return first, last
        
        initial = -1
        found = -1
        increments = 0
        for index in range(len(list_of_indexes)-1):
            #print(index)
            if found==-1:
                for x in list_of_indexes[index]:
                    if x+1 in list_of_indexes[index+1]:
                        if initial == -1:
                            initial = x
                        found = x+1
                        increments+=1
                        break
            else:
                if found+1 in list_of_indexes[index+1]:
                    found+=1
                    increments+=1
                else:
                    #print(found+1, list_of_indexes[index+1])
                    found=-1
                    #print("found is -1")
        if increments >1:
            first = initial - corresponding_indexes[0]
            last = first + length
            if length < corresponding_indexes[len(corresponding_indexes)-1]:
                last = first + corresponding_indexes[len(corresponding_indexes)-1]
            #print("positions areee")
            #print(first, last)
            return first, last
        else:
            return -1, -1




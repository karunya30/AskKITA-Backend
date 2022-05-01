import queue
from random import sample
from pygments import highlight
import sounddevice as sd
import vosk
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import  QCoreApplication
from LiveSubtitleWidget import LiveSubtitleWidget
vosk.SetLogLevel(-1)
import sys
import json
import pyautogui
import os
import time
import pytesseract
from PIL import Image
import re
import numpy as np
import cv2

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class VoskModel():
    def __init__(self, lang, model_path, mode='transcription', safety_word='stop' ):
        self.model_path = model_path#self._get_model_path()
        self.q = queue.Queue()
        self.previous_line = ""
        self.previous_length = 0
        self.mode = mode
        self.safety_word = safety_word
        self.lang = lang
        self.rec = ""
        self.text_dict = {}
        self.co_ord_list = []
        self.last_index = -1
        self.first_index = -1
        self.match = False
    def setUp(self):
        
        if not os.path.exists(self.model_path):
            print("Please download a model for your language from https://alphacephei.com/vosk/models")
            print(f"and unpack into {self.model_path}.")
        print(self.model_path)
        device_info = sd.query_devices(kind='input')
        samplerate = int(device_info['default_samplerate'])
        location = self.model_path+ "\\"+ self.lang
        
        model = vosk.Model(location)

        rec = vosk.KaldiRecognizer(model, samplerate)
        print('#' * 80)
        print('Press Ctrl+C to stop the recording')
        print('#' * 80)
        return rec,samplerate
        
    

    def transcribe(self):
        rec,samplerate = self.setUp()
        try: 
            
            with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=None, dtype='int16', channels=1,
                                   callback=self._callback):

                initial = time.perf_counter()
                while True:
                   
                    data = self.q.get()
                    if rec.AcceptWaveform(data):
                        d = json.loads(rec.Result())
                    else:
                        d = json.loads(rec.PartialResult())
                    for key in d.keys():
                        if d[key]:
                            if d[key] != self.previous_line or key == 'text':
                                #print(d)
                                self._write(d)
                                if d[key] == self.safety_word : return
                                self.previous_line = d[key]

        except KeyboardInterrupt:
            print('\nDone -- KEYBOARDiNTERRUPT')
        except Exception as e:
            print('exception', e)

    
    def subtitle(self, font_size):
        print("hi before")
        app = QApplication(sys.argv)
        win = LiveSubtitleWidget(font_size)
        win.show()
        #win.update_label()
        #sys.exit(app.exec_())
        print("hello")
        rec,samplerate = self.setUp()
        try: 
            
            with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=None, dtype='int16', channels=1,
                                   callback=self._callback):

                initial = time.perf_counter()
                while True:
                   
                    data = self.q.get()
                    if rec.AcceptWaveform(data):
                        d = json.loads(rec.Result())
                    else:
                        d = json.loads(rec.PartialResult())
                    for key in d.keys():
                        if d[key]:
                            if d[key] != self.previous_line or key == 'text':
                                print(d)
                                if "text" in d:
                                    win.notificationText.setText(d["text"])
                                else:
                                    win.notificationText.setText(d["partial"])
                                win.adjust()
                                #win.update_label(d)
                                #self._write(d)
                                if d[key] == self.safety_word : return
                                self.previous_line = d[key]
                    QCoreApplication.processEvents()

        except KeyboardInterrupt:
            print('\nDone -- KEYBOARDiNTERRUPT')
        except Exception as e:
            print('exception', e)   

    def compare2text(self):
        rec,samplerate = self.setUp()
        try: 

            with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=None, dtype='int16', channels=1,
                                   callback=self._callback):
                initial = time.perf_counter()
                #cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
                img = pyautogui.screenshot()
                img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
                words = pytesseract.image_to_string(img, lang="eng") #"eng" needs to be replaced by variable
                data = pytesseract.image_to_data(img, output_type = pytesseract.Output.DICT, lang="eng")
                words_clean = re.sub(r'[^\w\s]', '', words).lower()
                splitted = words.split()
                splitted_clean = words_clean.split()
                #print("The screenshot read the following")
                
                self.co_ord_list = list(zip(data['text'], data['left'], data['top'], data['width'], data['height']))
                co_ord_list_len = len(self.co_ord_list)
                index = 0
                while index<co_ord_list_len:
                    if self.co_ord_list[index][0] .replace(" ", "") == "":
                        self.co_ord_list.pop(index)
                        co_ord_list_len = len(self.co_ord_list)
                    else:
                        index+=1
                

                while True:
                    #getting text time
                    sinceLastScreenshot = time.perf_counter()
                    if (sinceLastScreenshot - initial) > 5:
                        #print("new screenshot")
                        img = pyautogui.screenshot()
                        img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
                        words = pytesseract.image_to_string(img, lang="eng")
                        data = pytesseract.image_to_data(img, output_type = pytesseract.Output.DICT, lang="eng")
                        words_clean = re.sub(r'[^\w\s]', '', words).lower()
                        splitted = words.split()
                        splitted_clean = words_clean.split()

                        self.co_ord_list = list(zip(data['text'], data['left'], data['top'], data['width'], data['height']))
                        index = 0
                        co_ord_list_len = len(self.co_ord_list)
                        while index<co_ord_list_len:
                            if self.co_ord_list[index][0] .replace(" ", "") == "":
                                self.co_ord_list.pop(index)
                                co_ord_list_len = len(self.co_ord_list)
                            else:
                                index+=1
                        
                        initial = sinceLastScreenshot
                    data = self.q.get()
                    if rec.AcceptWaveform(data):
                        d = json.loads(rec.Result())
                    else:
                        d = json.loads(rec.PartialResult())
                    for key in d.keys():
                        if d[key]:
                            if d[key] != self.previous_line or key == 'text':
                                
                                if 'text' in d:
                                    self._compare(d, splitted, splitted_clean,data) #pass the splitted data
                                #splitted is the list of words
                                #indexes is a dictionary
                                
                                if d[key] == self.safety_word : return
                                self.previous_line = d[key]

        except KeyboardInterrupt:
            print('\nDone -- KEYBOARDiNTERRUPT')
        except Exception as e:
            print('exception', e)
        

    def _get_model_path(self):
        full_path = os.path.realpath(__file__)
        file_dir = os.path.dirname(full_path)
        model_path = os.path.join(file_dir, 'models/vosk') 
        return model_path

    def _callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
            sys.stdout.flush()
        self.q.put(bytes(indata))

    def _write(self, phrase):
        pyautogui.press('backspace', presses=self.previous_length)
        if 'text' in phrase:
            pyautogui.write(phrase['text'] + '\n')
            self.previous_length = 0
        else:
            pyautogui.write(phrase['partial'])
            self.previous_length = len(phrase['partial'])

    
    def _compare(self, phrase_said, list_of_words, cleaned_list_of_words,data):

        """ if partial and self.match = false:
        continue
    if text = self.match = false
    if previous first and current first match - self.match = true
    previous len and current length = number of indices you have to highlight 
    and current highlight function can do one at a time
        """

        
            
        words_said = phrase_said['text']
        
        phrase_said = words_said.split()
        length = len(phrase_said)
        
        cleaned_list_of_words = [s.replace("?","").replace(",","").replace(".","")
        .replace('"','').replace("!","").replace(":","").replace(";","") for s in list_of_words]
        
        print("we are comparing:", phrase_said)
        
            

        
        list_of_indexes = []
        i = 0
        corresponding_indexes = [] 
        for x in range(len(phrase_said)): 
            if phrase_said[x] in cleaned_list_of_words:
                list_of_indexes.append([i for i,val in enumerate(cleaned_list_of_words) if val==phrase_said[x]])
               
                i+=1
                corresponding_indexes.append(x)
        
        first, last = self.get_indexes(list_of_indexes, corresponding_indexes, length)


        if first!= -1:
            print("WHAT YOU JUST READ")
            print(" ".join(list_of_words[first:last]))
            
            self.highlight(first, last-1)
            
            
        

    
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
                   
                    found=-1


        if increments >1:
            first = initial - corresponding_indexes[0]
            last = first + length
            if length < corresponding_indexes[len(corresponding_indexes)-1]:
                last = first + corresponding_indexes[len(corresponding_indexes)-1]
            
            return first, last
        else:
            return -1, -1

        
    

    def highlight(self, first_word_index, last_word_index):
        pyautogui.moveTo(self.co_ord_list[first_word_index][1], self.co_ord_list[first_word_index][2], duration = 0.1)
        pyautogui.keyDown('shift')
        pyautogui.keyDown('ctrl')
        pyautogui.dragTo(self.co_ord_list[last_word_index][1]+self.co_ord_list[last_word_index][3], 
        self.co_ord_list[last_word_index][2]+self.co_ord_list[last_word_index][4], duration = 0.5)
        pyautogui.keyUp('shift')
        pyautogui.keyUp('ctrl')
            
            
    

                
            
        


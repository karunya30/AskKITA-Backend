import sys 
from ask_kita import Ask_KITA

# datas=[('C:\\Users\\karus\\AppData\\Local\\Packages\\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\\LocalCache\\local-packages\\Python39\\site-packages\\vosk', './vosk')],

#funReaders.exe en-US vosk subtitle "C:\Users\karus\Documents\Final Year\FYP\Sam - Askkita and sphinx integration\Ask-kita-poc\models\vosk"
#funReaders.exe en-US sphinx subtitle "C:\Users\karus\Documents\Final Year\FYP\Sam - Askkita and sphinx integration\Ask-kita-poc\models\sphinx"
 
lang = sys.argv[1]
model = sys.argv[2]
mode = sys.argv[3]
model_path = sys.argv[4]
font_size = int(sys.argv[5])

speech_engine = Ask_KITA(lang, model, model_path)

print("yaaayy it is workinggg")
if mode == "read":
    speech_engine.compare2text()
if mode=="transcribe":
    speech_engine.transcribe()
if mode == "subtitle":
    speech_engine.subtitle(font_size)




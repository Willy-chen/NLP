import speech_recognition as sr
from gtts import gTTS

# import urllib.request
# import sys
import os
# import random

__all__ = ['STT']

UPLOAD_FOLDER = "/data/willy/NLP/audios"

class STT():
    def __init__(self, sl, filename):
        self.sl = sl
        self.filename = os.path.join(UPLOAD_FOLDER, filename)
        self.recognizer = sr.Recognizer()
    
    def recognize(self):
        file = sr.AudioFile(self.filename)
        with file as source:
            try:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio, language = self.sl)
                return text
            except sr.UnknownValueError:
                print("Could not understand audio!")
            except sr.RequestError as e:
                print("Could not request results; {0}".format(e))
                    
        return ""
        
# def text2speech(text,tl):
#     tts=gTTS(text, lang=tl)
#     filename='gSTT.mp3'
#     tts.save(filename)
#     # os.remove(filename)
    
# def speech2text():    
#     print("Speak:")
#     audio = recognizer.listen(source)
#     try:
#         text = recognizer.recognize_google(audio, language=sl)
#         print("You said:", text)
#         return text
#     except sr.UnknownValueError:
#         print("Could not understand audio!")
#     except sr.RequestError as e:
#         print("Could not request results; {0}".format(e))

if __name__ == "__main__":
    # with microphone as source:
    #     recognizer.adjust_for_ambient_noise(source)    
    #     while True:
    #         text  = speech2text()
    #         if text is not None:
    #             text2speech(text,sl)
    #         if text=='exit':
    #             break;
    stt = STT("eng", "/data/willy/NLP/audios/temp.wav")
    result = stt.recognize()
    print(result)
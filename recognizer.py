#!/usr/bin/env python

import wave
from vosk import KaldiRecognizer, Model

class Recognizer():

    def __init__(self,model_path):

        self.model_path = model_path
        self.model = Model(self.model_path)

    def decode(self,filename):

        #Preparing audio file
        wf = wave.open(filename, "rb")

        # if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        #     print ("Audio file must be WAV format.")
        #     exit (1)

        text_lst =[]
        p_text_lst =[]

        rec = KaldiRecognizer(self.model,wf.getframerate())
        rec.SetWords(True)

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                text_lst.append(rec.Result())
            else:
                p_text_lst.append(rec.PartialResult())
            
        return p_text_lst[-1]
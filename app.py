import queue
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import font
from turtle import back
import wave
import sys
import os
import time
import threading
import subprocess
import codecs
import json
import math
from tkinter import ttk

import sv_ttk

import numpy as np
import spacy

# Audio
import pyaudio
import soundfile as sf
import sounddevice as sd

# Data
import pandas as pd
import csv

# Images
from PIL import Image, ImageTk

# Modules
from recognizer import Recognizer
from recorder import Recorder
from translate_to_pictos import translate_to_pictos
from utils import *

# TextToPicto
from database import *
from shallowAnalysis import shallow_linguistic_analysis, load_model
from Word import Word

# WSD
from method.neural.NeuralDisambiguator import NeuralDisambiguator
from ufsac.common.WordnetHelper import WordnetHelper

from vosk import SetLogLevel

SetLogLevel(-1)


class pictoApp:

    def __init__(self):
        # GUI initialization (Tk)
        self.root = tk.Tk()

        custom_font = font.Font(family="latin modern sansquotation", size=12)

        sv_ttk.set_theme("light")

        self.root.title("Voice2Picto")
        self.root.resizable(True, True)
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        self.root.geometry("%dx%d" % (width, height))

        # Image icons
        self.icon_micro = tk.PhotoImage(file="res/images/micro.png")
        self.icon_square = tk.PhotoImage(file="res/images/square.png")
        self.icon_ad_disabled = tk.PhotoImage(file="res/images/ad_disabled.png")
        self.icon_ad_enable = tk.PhotoImage(file="res/images/ad_enable.png")
        self.icon_ad_listening = tk.PhotoImage(file="res/images/ad_listening.png")

        # Frames
        self.frame_settings = ttk.Frame(self.root)  # highlightbackground="blue",highlightthickness=2)
        self.frame_settings.place(relx=0.78, y=0, relwidth=.2, relheight=.9)
        self.frame_pictos = ttk.Frame(self.root)  # highlightbackground="blue",highlightthickness=2)
        self.frame_pictos.place(x=0, y=0, relwidth=.8, relheight=.9)

        # Canvas
        self.pictos = tk.Canvas(self.frame_pictos, width=1250, height=450, highlightthickness=1,
                                highlightbackground='gray75')
        self.pictos.place(relx=.5, rely=.3, anchor=tk.CENTER)
        self.images = [None] * 15

        self.text_output = tk.Text(self.frame_pictos, height=4, width=100, bg="gray96", font=custom_font)
        self.text_output.config(padx=12, pady=12)
        self.text_output.place(relx=.5, rely=.65, anchor=tk.CENTER)

        self.text_timing = tk.Text(self.frame_settings, height=3, width=20, bg="gold", font=custom_font)
        self.text_timing.config(padx=12, pady=12)
        self.text_timing.place(relx=.5, rely=.64, anchor=tk.CENTER)

        # Mode selection (push to talk, detection, etc.)
        self.label_intro = ttk.Label(self.frame_settings, text="Sélection du mode :", font=custom_font)
        self.label_intro.place(relx=.5, rely=0.09, anchor=tk.CENTER)
        self.modes = ["Appuyez pour parler  ", "Détection de l'activité  "]
        self.selected_mode = tk.StringVar(self.frame_settings)
        self.selected_mode.set(self.modes[0])
        self.mode_menu = ttk.OptionMenu(self.frame_settings, self.selected_mode, self.modes[0], *self.modes,
                                        command=self.mode_switch)
        self.mode_menu.place(relx=.5, rely=0.13, anchor=tk.CENTER)

        # Microphone menu initialization
        self.label_intro = ttk.Label(self.frame_settings, text="Sélection du microphone :", font=custom_font)
        self.label_intro.place(relx=.5, rely=0.19, anchor=tk.CENTER)
        self.devices = self.get_microphones()
        self.selected_micro = tk.StringVar(self.frame_settings)
        self.selected_micro.set(self.devices[0])
        self.micro_menu = ttk.OptionMenu(self.frame_settings, self.selected_micro, self.devices[0], *self.devices)
        self.micro_menu.place(relx=.5, rely=0.23, anchor=tk.CENTER)

        # Energy threshold slider
        self.label_threshold = ttk.Label(self.frame_settings, text="Seuil d'énergie :", justify="center",
                                         font=custom_font)
        self.label_threshold.place(relx=.5, rely=0.29, anchor=tk.CENTER)
        self.slider_threshold = ttk.Scale(self.frame_settings, from_=0, to=200, orient=tk.HORIZONTAL)
        self.slider_threshold.set(100)
        self.slider_threshold.place(relx=.5, rely=0.33, anchor=tk.CENTER)

        # Record button initialization
        self.button_rec = tk.Button(self.frame_pictos, text="Click", command=self.record_click_handler_ptt,
                                    image=self.icon_micro, bd=0, activebackground=self.root.cget('bg'))
        self.button_rec.place(relx=.5, rely=.85, anchor=tk.CENTER)

        # Exit button initialization
        self.button_exit = ttk.Button(self.root, text="Exit", command=self.exit_handler)
        self.button_exit.place(relx=.9, rely=0.92, width=100, height=40)

        # Timer initialization
        self.label = ttk.Label(self.frame_pictos, text="00:00:00", font=custom_font)
        self.label.place(relx=.5, rely=.94, anchor=tk.CENTER)

        # Recording state initialization
        self.record_state = False
        self.rec_thread = None

        # Initialization of the recognizer (asr)
        self.reco = Recognizer("models/vosk-model-small-fr-0.22")
        print("*** Done loading the recognizer ***")

        # Audio
        self.recorder = Recorder()
        self.recorder.close()

        # WSD
        lowercase = True
        clear_text = False
        batch_size = 1
        filter_lemma = False
        sense_compression_clusters = None
        wn = WordnetHelper.wn30()
        self.neural_disambiguator = NeuralDisambiguator("models/wsd/data_wsd",
                                                        ["models/wsd/model_weights_wsd0_camembert_base"],
                                                        clear_text,
                                                        batch_size, wn=wn, hf_model="camembert-base")
        self.neural_disambiguator.lowercase_words = lowercase
        self.neural_disambiguator.filter_lemma = filter_lemma
        self.neural_disambiguator.reduced_output_vocabulary = sense_compression_clusters
        print("*** Done loading the wsd model ***")

        # Load pictogram arasaac dataset
        self.picto_table = load_picto_table("database/arasaac.fre30bis.csv")
        self.wn_table = parse_wn31_file("database/index.sense")

        # Loading NLP Spacy model
        self.nlp = load_model("fr_dep_news_trf")

        # Start the window
        self.root.mainloop()

    def mode_switch(self, *args):
        """Method to switch mode (push to talk / activity detection)"""

        if str(self.selected_mode.get()) == self.modes[0]:
            self.button_rec.config(image=self.icon_micro)
            self.button_rec.config(command=self.record_click_handler_ptt)
            self.label.place(relx=.5, rely=.87, anchor=tk.CENTER)

        elif str(self.selected_mode.get()) == self.modes[1]:
            self.button_rec.config(image=self.icon_ad_disabled)
            self.button_rec.config(command=self.record_click_handler_ad)
            self.label.place_forget()

    def get_microphones(self):
        """Method to get the list of available record devices"""

        devices = []

        for device in sd.query_devices():
            if device['max_input_channels'] > 0:
                devices.append(device['name'] + "  ")

        return devices

    def record_click_handler(self, image, target, image2):
        # Start recording
        if not self.record_state:
            self.record_state = True
            self.button_rec.config(image=image)
            self.mode_menu.config(state=tk.DISABLED)

            # Prepare the recording thread in push to talk mode.
            self.rec_thread = threading.Thread(target=target)

            # Launch the recording thread
            self.rec_thread.start()

        # End recording
        else:
            self.record_state = False
            # Disable the record button
            self.button_rec.config(state=tk.DISABLED)
            self.button_rec.config(image=image2)

    def record_click_handler_ptt(self):
        """Handler to begin recording or end recording following the state"""
        self.record_click_handler(self.icon_square, self.listen_push_to_talk, self.icon_micro)

    def record_click_handler_ad(self):
        """Handler to begin recording or end recording following the state"""
        self.record_click_handler(self.icon_ad_enable, self.listen_activity_detection, self.icon_ad_disabled)

    def display_pictograms(self, text):
        """Method to display corresponding pictograms"""

        print("*** Starting displaying pictos ***")

        if text == "":
            return

        # Apply shallow linguistic analysis to get the modified sentences
        picto_ids, picto_lemmas = translate_to_pictos(text, self.neural_disambiguator, self.picto_table, self.wn_table,
                                                      self.nlp)

        slot_max_row = 7
        space = 170

        j = 0
        end_row = 0

        for i in range(len(picto_ids)):

            end_row = end_row + 1

            if end_row > slot_max_row:
                j = j + 1
                end_row = 0
            x = 100 + space * (i - slot_max_row * j)
            y = 100 + ((space + 50) * math.floor(i / slot_max_row))
            # Get the id and then get the image
            picto_id = picto_ids[i]

            # Get the image path and prepare the image to display it
            img_path = '/home/cecilemacaire/Bureau/Cloud/PROPICTO_RESSOURCES/ARASAAC/ARASAAC_Pictos_All/' + str(
                picto_id) + '.png'

            self.images[i] = Image.open(img_path)
            width, height = self.images[i].size
            new_width = 150  # largeur souhaitée
            new_height = int(new_width * height / width)  # hauteur proportionnelle
            resized_img = self.images[i].resize((new_width, new_height), resample=Image.BICUBIC)
            self.images[i] = ImageTk.PhotoImage(resized_img)

            # Display the word and the image
            self.pictos.create_image(x, y, image=self.images[i])
            if picto_lemmas[i] != "":
                self.pictos.create_text(x, y + 90, text=picto_lemmas[i], fill="black")

    def exit_handler(self):
        """Handler to exit the application when clicking on "exit" button"""

        sys.exit()

    def listen_activity_detection(self):
        """Method to record until the record state becomes False from activity detection"""

        while self.record_state:

            self.recorder.open()
            self.text_output.config(state=tk.NORMAL)
            self.text_timing.config(state=tk.NORMAL)

            # Read the stream and compare with the threshold limit
            data = self.recorder.stream.read(1024)
            rms_val = self.recorder.rms(data)
            if rms_val > self.slider_threshold.get():
                self.text_output.delete(1.0, tk.END)
                self.text_timing.delete(1.0, tk.END)
                self.pictos.delete("all")
                self.button_rec.config(image=self.icon_ad_listening)

                # Recorder record the segment until end of detection (s)
                self.recorder.record(self.slider_threshold.get())

                self.recorder.close()

                self.button_rec.config(image=self.icon_ad_enable)

                asr_time_start = time.time()

                # Decode
                transcription = clean_transcription(self.reco.decode("tmp/output.wav"))

                self.text_output.insert(tk.END, f"Parole reçue : {transcription}")
                self.text_output.insert(tk.END, f"\nTraduction en cours ...")
                self.text_output.config(state=tk.DISABLED)

                # Display pictograms
                self.display_pictograms(transcription)
                print("*** Done displaying pictograms ***")

                self.text_timing.insert(tk.END, f"Temps de décodage : \n{int(time.time() - asr_time_start):02d}s")
                self.text_timing.config(state=tk.DISABLED)

        # Enable the record button
        self.button_rec.config(image=self.icon_ad_disabled)
        self.button_rec.config(state=tk.NORMAL)
        self.mode_menu.config(state=tk.NORMAL)

    def listen_push_to_talk(self):
        """Method to record until the record state becomes False from push to talk"""

        # Begin timer
        start = time.time()
        self.text_output.config(state=tk.NORMAL)
        self.text_timing.config(state=tk.NORMAL)
        self.text_output.delete(1.0, tk.END)
        self.text_timing.delete(1.0, tk.END)
        self.pictos.delete("all")

        # Initialize audio recorder and stream
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        frames = []

        while self.record_state:
            data = stream.read(1024)
            frames.append(data)

            # Update the label of the timer
            passed = time.time() - start
            s = passed % 60
            m = passed // 60
            h = m // 60
            self.label.config(text=f"{int(h):02d}:{int(m):02d}:{int(s):02d}")

        # Close stream
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # Audio (WAV) file
        soundfile = wave.open("tmp/output.wav", "wb")
        soundfile.setnchannels(1)
        soundfile.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        soundfile.setframerate(44100)
        soundfile.writeframes(b"".join(frames))
        soundfile.close()

        self.label.config(text="00:00:00")

        asr_time_start = time.time()

        # Decode
        transcription = clean_transcription(self.reco.decode("tmp/output.wav"))

        self.text_output.insert(tk.END, f"Parole reçue : {transcription}")
        self.text_output.insert(tk.END, f"\nTraduction en cours ...")
        self.text_output.config(state=tk.DISABLED)

        # Display pictograms
        self.display_pictograms(transcription)
        print("*** Done displaying pictograms ***")

        self.text_timing.insert(tk.END, f"Temps de décodage : \n{int(time.time() - asr_time_start):02d}s")
        self.text_timing.config(state=tk.DISABLED)

        # Enable the record button
        self.button_rec.config(state=tk.NORMAL)
        self.mode_menu.config(state=tk.NORMAL)


if __name__ == "__main__":
    pictoApp()

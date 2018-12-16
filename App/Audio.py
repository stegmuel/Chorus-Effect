try:
    # for Python2
    from Tkinter import *   ## notice capitalized T in Tkinter 
except ImportError:
    # for Python3
    from tkinter import *

from scipy.signal import resample, blackmanharris, triang
from tkinter import ttk
from tkinter import filedialog 
import os
#from playsound import playsound
#import auxFun as aux
#import pitchShift as ptch
import wave
import pyaudio
#import time
import SoundFun
import numpy as np
from scipy.io import wavfile
#import auxFun

from struct import pack
from math import sin, pi
import sounddevice as sd


class Root(Tk):
	def __init__(self):
		super(Root, self).__init__()
		self.title("Chorus Effect")
		self.configure(bg = '#777777')
		self.minsize(400,400)

		self.filename = Entry(self)
		self.signal = []
		self.fs = None
		self.signal2Play = None
		self.Output = []
		self.effect = []
		self.recBool = 0

		self.browseFrame= ttk.LabelFrame(self, text = "Choose file...")
		self.browseFrame.grid(row=1, column=0, padx = 20, pady = 20)

		self.recLengthFrame = ttk.LabelFrame(self, text = "Record duration (sec.):")
		self.recLengthFrame.grid(row=1,column=2)
		self.recLength = Entry(self.recLengthFrame)
		self.recLength["width"] = 5
		self.recLength.grid(column=3, row=1)
		self.recLength.delete(0,END)
		self.recLength.insert(0, "5")

		self.recFrame = ttk.LabelFrame(self, text="Record")
		self.recFrame.grid(row=1, column=4, padx=20, pady=20)


		self.v = IntVar()
		self.v.set(0)  

		self.intensity1Frame = ttk.LabelFrame(self, text="Intensity 1")
		self.intensity1Frame.grid(row=7, column=0, padx=20, pady=20)
		self.int1_s = Scale(self.intensity1Frame, from_=0.1, to=0, resolution=0.01)
		self.int1_s.set(0.05)
		self.int1_s.grid(row=7, column=0)
		
		self.rate1Frame = ttk.LabelFrame(self, text="Rate 1")
		self.rate1Frame.grid(row=7, column=1, padx=20, pady=20)	
		self.rate1_s = Scale(self.rate1Frame, from_=10, to=0, resolution=0.5)
		self.rate1_s.set(5)
		self.rate1_s.grid(row=7, column=1)

		self.intensity2Frame = ttk.LabelFrame(self, text="Intensity 2")
		self.intensity2Frame.grid(row=7, column=2, padx=20, pady=20)
		self.int2_s = Scale(self.intensity2Frame, from_=0.1, to=0, resolution=0.01)
		self.int2_s.set(0.05)
		self.int2_s.grid(row=7, column=2)

		self.rate2Frame = ttk.LabelFrame(self, text="Rate 2")
		self.rate2Frame.grid(row=7, column=3, padx=20, pady=20)	
		self.rate2_s = Scale(self.rate2Frame, from_=10, to=0, resolution=0.5)
		self.rate2_s.set(5)
		self.rate2_s.grid(row=7, column=3)

		self.wetFrame = ttk.LabelFrame(self, text="Wet")
		self.wetFrame.grid(row=7, column=4, padx=20, pady=20)	
		self.wet_s = Scale(self.wetFrame, from_=1, to=0, resolution=0.1)
		self.wet_s.set(0.5)
		self.wet_s.grid(row=7, column=4)

		self.pan1Frame = ttk.LabelFrame(self, text="Pan 1")
		self.pan1Frame.grid(row=10, column=0, padx=20, pady=20)
		self.pan1 = Scale(self.pan1Frame, from_=-10, to=10, resolution=0.5, orient=HORIZONTAL)
		self.pan1.set(-5)
		self.pan1.grid(row=10, column=0)

		self.pan2Frame = ttk.LabelFrame(self, text="Pan 2")
		self.pan2Frame.grid(row=10, column=2, padx=20, pady=20)
		self.pan2 = Scale(self.pan2Frame, from_=-10, to=10, resolution=0.5, orient=HORIZONTAL)
		self.pan2.set(5)
		self.pan2.grid(row=10, column=2)

		
		self.playFrame= ttk.LabelFrame(self)
		self.playFrame.grid(row=11, column = 4)

		self.selectFrame = ttk.LabelFrame(self, text = "Effect")
		self.selectFrame.grid(row=10, column = 4)

		languages = [
		    ("No", "effect"),
		    ("Robot"),
                    ("Alien")
		]


		i = 10
		for val, language in enumerate(languages):
			Radiobutton(self.selectFrame,
				        text=language,
						padx = 20,
				  		variable=self.v,
				  		value=val).grid(row=i,  sticky = W+E)
			i = i+1

		self.browse()
		self.rec()
		self.playButton()
		self.stopButton()
		self.save()
		
	
                
	def browse(self):
		self.browse = ttk.Button(self.browseFrame, text = "Browse", command = self.fileDialog)
		self.browse.grid(column=1, row=1)

	def save(self):
		self.save = ttk.Button(self.playFrame, text = "Save", command = lambda: self.SavefileDialog())
		self.save.grid(column=0, row=11)


	def rec(self):
		self.rec = ttk.Button(self.recFrame, text = "Rec", command = lambda: self.record())
		self.rec.grid(column=2, row=1)

	def record(self):
		self.signal, self.fs = SoundFun.recAndPlay(self)
		self.recBool = 1
		print(self.signal.shape)
		print(self.fs)

	def fileDialog(self):
		#global InSignal
		self.filename = filedialog.askopenfilename(initialdir = "./", title = "Select a file", filetypes = (("wave", "*.wav"), ("All files", "*.*")))
		self.label = ttk.Label(self.browseFrame, text = "")
		self.label.grid(row=2,sticky = W+E, column = 1)
		base=os.path.basename(self.filename)
		self.label.configure(text = base)
		#InSignal = wave.open(self.filename, 'rb')
		#self.signal2Play = wave.open(self.filename, 'rb')
		self.fs, self.signal = wavfile.read(self.filename)
		#self.signal = np.asarray(self.signal, dtype=np.int16)
		self.recBool = 0

	def SavefileDialog(self):
                self.computeOutput()
                self.filename = filedialog.asksaveasfilename(initialdir = "./", title = "Select a file", filetypes = (("wave", "*.wav"), ("All files", "*.*")))
                self.label = ttk.Label(self.playFrame, text = "")
                self.label.grid(column=0, row=11)
                #self.Output = np.asarray(self.Output, dtype=np.float32)
                wavfile.write(self.filename, self.fs, self.Output)


	def playButton(self):
		#global InSignal
		#global OutSignal
		##self.play = ttk.Button(self.playFrame, text = "Play", command = lambda:aux.wavplay(self.filename))
		#OutSignal = ptch.DFT_pshift(InSignal, 0.9, ptch.ms2smp(30, fs),.2)
		#print(np.array(self.signal).size())
		self.play = ttk.Button(self.playFrame, text = "Play", command = lambda: self.playAux())
		self.play.grid(column=0, row=5)

	def stopButton(self):
                self.stop = ttk.Button(self.playFrame, text = "Stop", command = lambda: self.stopAux())
                self.stop.grid(column=0, row=10)

	def playAux(self):

            self.computeOutput()
            #self.stereoTest()

            SoundFun.play(self.Output, self.fs)

	def computeOutput(self):
            if(self.v.get()==1):
                print(np.max(self.signal))
                self.effect= SoundFun.robot_voice(self.signal, 100, self.fs)
                print(np.max(self.signal))
            elif(self.v.get()==2):
                self.effect=SoundFun.alien_voice(self.signal, 100, self.fs)
            else:
                self.effect = self.signal

            self.Output = SoundFun.chorusAux(self.effect, self.fs, float(self.int1_s.get()),float(self.int2_s.get()), float(self.rate1_s.get()),float(self.rate2_s.get()),float(self.wet_s.get()),float(self.pan1.get()),float(self.pan2.get()))
            print(int(self.v.get()))

            #if(int(self.v.get())==1):
                #self.Output = SoundFun.alien_voice(self.Output, 100, self.fs)

            self.Output = np.asarray(self.Output, dtype=np.int16)
            print(self.Output)


			
	def stopAux(self):
		SoundFun.stop()
                
'''
	def stereoTest(self):
		freq = 440.0
		freq2 = 700.0
		data_size = 40000
		fname = "WaveTest.wav"
		frate = 11025.0  # framerate as a float
		amp = 64000.0     # multiplier for amplitude

		sine_list_x = []
		sine_list_x2 = []
		for x in range(data_size):
			sine_list_x.append(sin(2*pi*freq*(x/frate)))
			sine_list_x2.append(sin(2*pi*freq2*(x/frate)))

		wav_file = wave.open(fname, "w")

		nchannels = 2
		sampwidth = 2
		framerate = int(frate)
		nframes = data_size
		comptype = "NONE"
		compname = "not compressed"

		wav_file.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))

		for s, t in zip(sine_list_x, sine_list_x2):
			# write the audio frames to file
			wav_file.writeframes(pack('h', int(s*amp/2)))
			wav_file.writeframes(pack('h', int(t*amp/2)))

		wav_file.close()
'''	


if __name__ == '__main__':
	root = Root()
	root.mainloop()

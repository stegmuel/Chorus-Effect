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
import wave
import SoundFun
import numpy as np
from scipy.io import wavfile


from math import sin, pi

class Root(Tk):
	def __init__(self):
		super(Root, self).__init__()
		self.title("Chorus Effect")
		self.configure(bg = '#CCCCCC')
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
		self.int1_s.set(0.01)
		self.int1_s.grid(row=7, column=0)
		
		self.rate1Frame = ttk.LabelFrame(self, text="Rate 1")
		self.rate1Frame.grid(row=7, column=1, padx=20, pady=20)	
		self.rate1_s = Scale(self.rate1Frame, from_=10, to=0, resolution=0.5)
		self.rate1_s.set(2.5)
		self.rate1_s.grid(row=7, column=1)

		self.intensity2Frame = ttk.LabelFrame(self, text="Intensity 2")
		self.intensity2Frame.grid(row=7, column=2, padx=20, pady=20)
		self.int2_s = Scale(self.intensity2Frame, from_=0.1, to=0, resolution=0.01)
		self.int2_s.set(0.03)
		self.int2_s.grid(row=7, column=2)

		self.rate2Frame = ttk.LabelFrame(self, text="Rate 2")
		self.rate2Frame.grid(row=7, column=3, padx=20, pady=20)	
		self.rate2_s = Scale(self.rate2Frame, from_=10, to=0, resolution=0.5)
		self.rate2_s.set(7)
		self.rate2_s.grid(row=7, column=3)

		self.wetFrame = ttk.LabelFrame(self, text="Wet")
		self.wetFrame.grid(row=7, column=4, padx=20, pady=20)	
		self.wet_s = Scale(self.wetFrame, from_=1, to=0, resolution=0.1)
		self.wet_s.set(0.8)
		self.wet_s.grid(row=7, column=4)

		self.pan1Frame = ttk.LabelFrame(self, text="Pan 1")
		self.pan1Frame.grid(row=10, column=0, padx=20, pady=20)
		self.pan1 = Scale(self.pan1Frame, from_=-10, to=10, resolution=0.5, orient=HORIZONTAL)
		self.pan1.set(-6)
		self.pan1.grid(row=10, column=0)

		self.pan2Frame = ttk.LabelFrame(self, text="Pan 2")
		self.pan2Frame.grid(row=10, column=2, padx=20, pady=20)
		self.pan2 = Scale(self.pan2Frame, from_=-10, to=10, resolution=0.5, orient=HORIZONTAL)
		self.pan2.set(6)
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
		self.filename = filedialog.askopenfilename(initialdir = "./", title = "Select a file", filetypes = (("wave", "*.wav"), ("All files", "*.*")))
		self.label = ttk.Label(self.browseFrame, text = "")
		self.label.grid(row=2,sticky = W+E, column = 1)
		base=os.path.basename(self.filename)
		self.label.configure(text = base)
		self.fs, self.signal = wavfile.read(self.filename)
		self.recBool = 0

	def SavefileDialog(self):
                self.computeOutput()
                self.filename = filedialog.asksaveasfilename(initialdir = "./", title = "Select a file", filetypes = (("wave", "*.wav"), ("All files", "*.*")))
                self.label = ttk.Label(self.playFrame, text = "")
                self.label.grid(column=0, row=11)
                wavfile.write(self.filename, self.fs, self.Output)


	def playButton(self):
		self.play = ttk.Button(self.playFrame, text = "Play", command = lambda: self.playAux())
		self.play.grid(column=0, row=5)

	def stopButton(self):
                self.stop = ttk.Button(self.playFrame, text = "Stop", command = lambda: self.stopAux())
                self.stop.grid(column=0, row=10)

	def playAux(self):
            self.computeOutput()
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
            self.Output = np.asarray(self.Output, dtype=np.int16)
            print(self.Output)


			
	def stopAux(self):
		SoundFun.stop()

if __name__ == '__main__':
	root = Root()
	root.mainloop()

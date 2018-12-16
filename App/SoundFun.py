import pyaudio
import time
import numpy as np
import scipy as sp
import sounddevice as sd

def play(signal, fs):
	#fade_in = np.linspace(0,1,256)
	#signal[0:256] = signal[0:256]*fade_in
	#print(signal)
        sd.play(signal, fs)

def stop():
	sd.stop()

def recAndPlay(self):
	fs = 8000
	print(self.recLength.get())
	duration = int(self.recLength.get())+0.75  # seconds
	myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
	sd.wait()

	#test = np.transpose(myrecording)
	
	#out = chorus_effect(test[0,], fs, float(self.int1_s.get()), float(self.int2_s.get()), float(self.rate1_s.get()), float(self.rate2_s.get()), float(self.wet_s.get()))
	
	#fade_in = np.linspace(0,1,128)
	#out = np.transpose(out)
	#out[0:128] = out[0:128]*fade_in

	#sd.play(out, fs)
	#play(np.transpose(out),fs)
	return (np.transpose(myrecording)[0,6000:], fs)

def playData(samples):
	p=pyaudio.PyAudio() 
	stream = p.open(format=pyaudio.paFloat32,
                		 channels=1,
                         rate=8000,
                         output=True,
                         output_device_index=1
                         )
	# Assuming you have a numpy array called samples
	data = samples.astype(np.float32).tostring()
	stream.write(data)

def play_audio2(wf):
	##wf = wave.open('singing_8000.wav', 'rb')

	# instantiate PyAudio (1)
	p = pyaudio.PyAudio()

	# define callback (2)
	def callback(in_data, frame_count, time_info, status):
	    data = wf.readframes(frame_count)
	    return (data, pyaudio.paContinue)

	# open stream using callback (3)
	stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
		        channels=wf.getnchannels(),
		        rate=wf.getframerate(),
		        output=True,
		        stream_callback=callback)

	# start the stream (4)
	stream.start_stream()

	# wait for stream to finish (5)
	while stream.is_active():
	    time.sleep(0.1)

	# stop stream (6)
	stream.stop_stream()
	stream.close()
	wf.close()

	# close PyAudio (7)
	p.terminate()

def time_stretch(signal,alpha):
	epsilon = 1e-9;
	N=int(2**7) 
	M=int(2**7)
	Rs= int(2**7/8)
	w=np.hanning(2**7)
	Ra = int(Rs / float(alpha))

	hM1 = int(np.floor((M-1)/2.))
	hM2 = int(np.floor(M/2.))

	wscale = sum([i**2 for i in w]) / float(Rs)
	L = signal.size
	L0 = int(signal.size*alpha)


	A = np.fft.fft(w*signal[0:N])
	B = np.fft.fft(w*signal[Ra:Ra+N])
	Freq0 = B/A * abs(B/A)
	Freq0[Freq0 == 0] = epsilon

	signal = np.append(np.zeros(int(len(w))), signal)
	#signal = np.append(signal,np.zeros(int(len(w))))

	time_stretch_signal = np.zeros(int((signal.size)*alpha + signal.size/Ra * alpha))
	#time_stretch_signal = np.zeros(int((signal.size)*alpha))

	p, pp = 0, 0
	pend = signal.size - (Rs+N)
	Yold = epsilon

	i = 0
	while p <= pend:
		i += 1
		# Spectra of two consecutive windows    
		a = w*signal[p+Rs:p+Rs+N]
		Xs = np.fft.fft(w*signal[p:p+N])
		Xt = np.fft.fft(w*signal[p+Rs:p+Rs+N])

		# Prohibit dividing by zero
		Xs[Xs == 0] = epsilon
		Xt[Xt == 0] = epsilon

		# inverse FFT and overlap-add
		if p > 0 :
			Y = Xt * (Yold / Xs) / abs(Yold / Xs)
		else:
			Y = Xt * Freq0

		Yold = Y
		Yold[Yold == 0] = epsilon

		time_stretch_signal[pp:pp+N] = np.add(time_stretch_signal[pp:pp+N], w*np.fft.ifft(Y), out=time_stretch_signal[pp:pp+N], casting="unsafe")

		p = int(p+Ra)		# analysis hop
		pp += Rs			# synthesis hop

	time_stretch_signal = time_stretch_signal / wscale    
	# retrieve input signal perfectly
	#signal = np.delete(signal, range(2000))

	time_stretch_signal = np.delete(time_stretch_signal, range(Rs))
	time_stretch_signal = np.delete(time_stretch_signal, range(L0, time_stretch_signal.size))
	#time_stretch_signal = np.delete(time_stretch_signal, range(len(time_stretch_signal)-int(alpha*len(w)),len(time_stretch_signal)))
	
	return time_stretch_signal

def time_varying_pitch(signal, fs, intensity, rate):
	N = int(rate*len(signal)/fs)
	alpha_max = 1.1
	overlap = 400
	safety = 200
	effective_window = 1000
	length_window = effective_window + overlap + 2*safety
	n = int(len(signal)/effective_window)
	fade_in = np.linspace(0,1,overlap)
	fade_out = np.linspace(1,0,overlap)
	time_stretch_resample = []
	window_resample = []
	
	for i in range(n):
		alpha = 1 + intensity*np.sin(2*N*np.pi*i/n)

		low_index = i*effective_window
		high_index = i*effective_window + length_window
		
		time_stretched_window = time_stretch(signal[low_index:high_index], alpha)
		
		# delete safety margins
		time_stretched_window = np.delete(time_stretched_window,range(len(time_stretched_window)-int(safety*alpha),len(time_stretched_window)))
		time_stretched_window = np.delete(time_stretched_window,range(0,int(safety*alpha)))

		#pitch, #append, #overlap
		window_resample = sp.signal.resample(time_stretched_window,effective_window+overlap)

		if i==0:
			time_stretch_resample = window_resample
			#fade out
			time_stretch_resample[effective_window:effective_window+overlap] *= fade_out
			
		if i>0:
			# fade in - fade out
			window_resample[0:overlap] *= fade_in
			window_resample[effective_window:effective_window+overlap] *= fade_out
			time_stretch_resample[len(time_stretch_resample)-overlap:len(time_stretch_resample)] += window_resample[0:overlap]
			time_stretch_resample = np.append(time_stretch_resample, window_resample[overlap:])
			#print(len(time_stretch_resample))
			#time_stretch_signal = time_stretch(signal[int(np.floor((i)*len(signal)/n)) : int(np.floor((i+1)*len(signal)/n))],alpha)
			### Here ###
			#play(time_stretch_resample[int((i-1)*1.5)*len(window_resample):int(i*1.5)*len(window_resample)],fs)
			### Here ###
			#time_stretch_signal = signal[int(np.floor((i)*len(signal)/n)):int(np.floor((i+1)*len(signal)/n))]
			#time_stretch_resample = np.append(time_stretch_resample, rescale(time_stretch_signal, 1/alpha))
		
     
	time_stretch_resample = np.append(signal[0:safety-64],time_stretch_resample)
		
	return time_stretch_resample

def chorus_effect(signal, fs, intensity1, intensity2, rate1, rate2, wet):

	chorus_signal_1 = time_varying_pitch(signal, fs, intensity1, rate1)
	chorus_signal_2 = time_varying_pitch(signal, fs, intensity2, rate2)

	chorus = float(0.5)*wet*chorus_signal_1[0:min(len(chorus_signal_1), len(signal))] + float(0.5)*wet*chorus_signal_2[0:min(len(chorus_signal_2), len(signal))] + (1-wet)*signal[0:min(len(chorus_signal_1), len(signal))]

	return chorus

def robot_voice(signal, f, fs):
    w = (float(f) / fs) * 2 * np.pi  # normalized modulation frequency
    return 2 * np.multiply(signal, np.cos(w * np.arange(0,len(signal))))

def alien_voice(signal, fshift, fs):
    shift = int(fshift/fs*len(signal));
    signal_fft = np.fft.rfft(signal);
    signal_fft_rolled = np.roll(signal_fft, shift);
    signal_fft_rolled[0:shift] = 0;
    signal_pitched = np.fft.irfft(signal_fft_rolled)
    
    return signal_pitched
    
def chorusAux(signal, fs, intensity1, intensity2, rate1, rate2, wet, pan1, pan2):
	chorus_signal_1 = time_varying_pitch(signal, fs, intensity1, rate1)
	chorus_signal_2 = time_varying_pitch(signal, fs, intensity2, rate2)

	scale_right1 = (10+pan1)/20
	scale_left1 = 1-scale_right1
	scale_right2 = (10+pan2)/20
	scale_left2 = 1-scale_right2

	signal_left = wet/2*scale_left1*chorus_signal_1[0:min(len(chorus_signal_1), len(signal))] + wet/2*scale_left2*chorus_signal_2[0:min(len(chorus_signal_1), len(signal))] +(1-wet)*signal[0:min(len(chorus_signal_1), len(signal))]
	signal_right = wet/2*scale_right1*chorus_signal_1[0:min(len(chorus_signal_1), len(signal))] + wet/2*scale_right2*chorus_signal_2[0:min(len(chorus_signal_1), len(signal))] +(1-wet)*signal[0:min(len(chorus_signal_1), len(signal))]

	chorus = np.column_stack((signal_left, signal_right))
	return chorus


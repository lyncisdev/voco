import sys
import wave
import pyaudio
import audioop
import unicodedata
import time
import numpy as np
import os
import re


basedir= "decode/data/"

mic = -1
chunk = 0
byterate = 16000
pa = pyaudio.PyAudio()
sample_rate = byterate
stream = None
debug=False

print("----------------------------line 24")
outputfile=open(basedir + 'spk2gender','w')
outputfile.write("bartek m \n")


naming_list_counter = 1

line = "xxxx01 cmplx x-ray charlie" 


command = re.findall(r'\S+', line)

UID = str(naming_list_counter).zfill(5) + "_" + "".join(command[0])

if debug:
	print("UID: " + UID)


phrase = "x-ray charlie";

	
raw_input("Press enter to start...")		




# wait to avoid keyboard sound

time.sleep(0.2)
print("recording")	

# open stream

try:
	# try adjusting this if you want fewer network packets
	chunk = 512 * 2 * sample_rate / byterate

	if mic == -1:
		mic = pa.get_default_input_device_info()['index']
		if debug:			    
			print >> sys.stderr, "Selecting default mic"
	if debug:
		print >> sys.stderr, "Using mic #", mic
	stream = pa.open(
	    rate = sample_rate,
	    format = pyaudio.paInt16,
	    channels = 1,
	    input = True,
	    input_device_index = mic,
	    frames_per_buffer = chunk)

except IOError, e:
	if(e.errno == -9997 or e.errno == 'Invalid sample rate'):
	    new_sample_rate = int(pa.get_device_info_by_index(mic)['defaultSampleRate'])
	    if(sample_rate != new_sample_rate):
		sample_rate = new_sample_rate
	print >> sys.stderr, "\n", e
	print >> sys.stderr, "\nCould not open microphone. Please try a different device."
	global fatal_error
	fatal_error = True
	sys.exit(0)

	print >> sys.stderr, "\nLISTENING TO MICROPHONE"
	last_state = None




# record while talking
gate = 600
window_length = 8
rms = [gate]*window_length		
audio_sample = []
audio_sample_recording_list_counter = 0

#for x in range(0, 100):
while max(rms) >= gate:
	for i in range(0,window_length-1):
		rms[i] = rms[i+1]

	data = stream.read(chunk)
	rms[window_length-1] = audioop.rms(data, 2)

	audio_sample.append(data)
	audio_sample_recording_list_counter += 1

	# print RMS graph
	#bars = (rms[window_length-1] - gate)/100
	#for x in range(0, bars):
	#	print "=",
	#print("")

	if debug:
		print(audio_sample_recording_list_counter, rms)

if debug:
	print("stopping stream")

stream.stop_stream()

# Normalize audio
new_audio_sample = []
audio_sample_recording_list_counter = 0
rms = []

for x in audio_sample:
	rms.append(audioop.rms(x, 2))

sample_mean = np.mean(rms)
scaling_factor = 4000/sample_mean

if debug:
	print(scaling_factor)

for x in audio_sample:
	new_audio_sample.append(audioop.mul(x, 2,scaling_factor))


audio_sample = new_audio_sample


# Write audio audio_records/naming_list_counter.txt

audio_sample_file_path = "/home/bartek/Projects/ASR/kaldi_mar_17/egs/digits/decode/data/" + UID + ".wav"
audio_sample_file = open(audio_sample_file_path, 'w+')

w = wave.open(audio_sample_file_path,"w")
w.setnchannels(1)
w.setsampwidth(2)
w.setframerate(byterate)

for x in new_audio_sample:
	w.writeframes(x)

w.close()

#time.sleep(0.5)
#os.system("aplay " + audio_sample_file_path)




#file_list = ["data/spk2gender","data/wav.scp","data/text","data/utt2spk","data/corpus.txt"]

outputfile=open(basedir + 'wav.scp','w')
outputfile.write(UID + " " + audio_sample_file_path  + "\n")

outputfile=open(basedir + 'text','w')
outputfile.write(UID + " " + phrase + "\n")

outputfile=open(basedir + 'utt2spk','w')
outputfile.write(UID + " bartek" + "\n")

outputfile=open(basedir + 'spk2utt','w')
outputfile.write("bartek " + UID + "\n")





















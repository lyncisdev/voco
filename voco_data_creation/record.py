#
# inputs
#	recording_list in the format of utt_list	<UID> \t <cat> \t <phrase>
#	recording_list_counter
#	naming_list_counter
# output
# 	in audio_records folder
#		spk2gender
#		wav.scp
#		text
#		utt2spk
#		corpus.txt
#	
#	in audio_data folder
#		individual recodings named as <naming_list_counter>_<uid>
#	
#	
#	

import sys
import wave
import pyaudio
import audioop
import unicodedata
import time
import numpy as np
import os
import re



mic = -1
chunk = 0
byterate = 16000
pa = pyaudio.PyAudio()
sample_rate = byterate
stream = None 
debug = False
word_accepted = False
breaking = False


recording_list_file = open('complex_recording_list.txt','r')

for x in range(0,40):
	print("")	


### initalize recording recording_list_counter

try:
    with open("recording_list_counter.txt") as f:
        recording_list_counter = int(f.read())
except IOError:
    recording_list_counter = 1


### initalize recording recording_list_counter

try:
    with open("audio_records/naming_list_counter.txt") as f:
        naming_list_counter = int(f.read())
except IOError:
    naming_list_counter = 1




### make sure audio records exist

#file_list = ["data/spk2gender","data/wav.scp","data/text","data/utt2spk","data/corpus.txt"]
#
#for f in file_list:
#	tmp=open(f,'a')


### create spk2gender
outputfile=open('audio_records/spk2gender','w')
outputfile.write("bartek m \n")


recording_list = recording_list_file.readlines()[recording_list_counter:]


for line in recording_list:
	
	if debug:
		print(line)
	command = re.findall(r'\S+', line)
	
	UID = str(naming_list_counter).zfill(5) + "_" + "".join(command[0])
	
	if debug:
		print("UID: " + UID)


	phrase = "";
	for x in command[2:]:
		phrase += "".join(x)
		phrase += " "
	
	if debug:	
		print(phrase)
		raw_input("wait")

	



	while word_accepted == False:


		print("--------------------------------" + str(recording_list_counter) + "--------------------------------")			
		print("")			
		print("Word:			" + phrase)			
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
				continue
			print >> sys.stderr, "\n", e
			print >> sys.stderr, "\nCould not open microphone. Please try a different device."
			global fatal_error
			fatal_error = True
			sys.exit(0)

			print >> sys.stderr, "\nLISTENING TO MICROPHONE"
			last_state = None




		# record while talking
		gate = 750
		window_length = 10
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

		audio_sample_file_path = "/home/bartek/Projects/ASR/model_training/audio_data/" + UID + ".wav"
 		audio_sample_file = open(audio_sample_file_path, 'w+')
		
		w = wave.open(audio_sample_file_path,"w")
		w.setnchannels(1)
		w.setsampwidth(2)
		w.setframerate(byterate)
	
		for x in new_audio_sample:
			w.writeframes(x)

		w.close()

		time.sleep(0.5)
		os.system("aplay " + audio_sample_file_path)

		accept = raw_input("accept?")
		if accept == "n":
			word_accepted = False
		elif accept == "end":
			breaking = True
			break	
		else:
			word_accepted = True
	
	

	if breaking:
		break
	word_accepted = False
	
	#file_list = ["data/spk2gender","data/wav.scp","data/text","data/utt2spk","data/corpus.txt"]

	outputfile=open('audio_records/wav.scp','a')
	outputfile.write(UID + " " + audio_sample_file_path  + "\n")

	outputfile=open('audio_records/text','a')
	outputfile.write(UID + " " + phrase + "\n")

	outputfile=open('audio_records/utt2spk','a')
	outputfile.write(UID + " bartek" + "\n")

	recording_list_counter += 1
	with open("recording_list_counter.txt", "w") as f:
		f.write(str(recording_list_counter))

	naming_list_counter += 1
	with open("audio_records/naming_list_counter.txt", "w") as f:
		f.write(str(naming_list_counter))



























import sys
import wave
import pyaudio
import audioop
import unicodedata
import time
import numpy as np
import os
import re
import subprocess
import pdb

from process_line import process_line
from scan import scan
from parse import parse
from execute import execute
from errors import GrammaticalError
from ast import printAST



basedir= "decode/data/"
debug=False

outputfile=open(basedir + 'spk2gender','w')
outputfile.write("bartek m \n")

#----------------------------------------------------------------------------
# write_audio_file function

def write_audio_data(audio_sample,audio_sample_file_path, byterate):
    
    new_audio_sample = []
    rms = []
    
    # calculate RMS of each point
    for x in audio_sample:
        rms.append(audioop.rms(x, 2))

    # calculate scaling factor
    sample_mean = np.mean(rms)
    scaling_factor = 4000/sample_mean

    # multiply samples by scaling factor
    for x in audio_sample:
        new_audio_sample.append(audioop.mul(x, 2,scaling_factor))

    # Write audio file
    audio_sample_file = open(audio_sample_file_path, 'w+')

    w = wave.open(audio_sample_file_path,"w")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(byterate)

    for x in new_audio_sample:
        w.writeframes(x)

    w.close()

#    time.sleep(0.5)
#    os.system("aplay " + audio_sample_file_path)


    
#----------------------------------------------------------------------------
# write_audio_file function

def write_audio_records(basedir,session_counter,audio_sample_file_path, UID):
    outputfile=open(basedir + 'wav_sample.scp','w')
    outputfile.write(UID + " " + audio_sample_file_path  + "\n")
    
    outputfile=open(basedir + 'wav.scp','a')
    outputfile.write(UID + " " + audio_sample_file_path  + "\n")
    
    #outputfile=open(basedir + 'text','w')
    #outputfile.write(UID + " " + phrase + "\n")

    #outputfile=open(basedir + 'utt2spk','w')
    #outputfile.write(UID + " bartek" + "\n")

    outputfile=open(basedir + 'utt2spk_sample','w')
    outputfile.write(UID + " bartek" + "\n")
    
    #outputfile=open(basedir + 'spk2utt','w')
    #outputfile.write("bartek " + UID + "\n")
    
    outputfile=open(basedir + 'spk2utt_sample','w')
    outputfile.write("bartek " + UID + "\n")
    
    with open("session_counter.txt", "w") as f:
        f.write(str(session_counter))
    
    
#----------------------------------------------------------------------------
# open stream

mic = -1
chunk = 0
byterate = 16000
pa = pyaudio.PyAudio()
sample_rate = byterate
stream = None
debug=False

try:
    # try adjusting this if you want fewer network packets
    chunk = 12 * 512 * 2 * sample_rate / byterate

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

#----------------------------------------------------------------------------

try:
    with open("session_counter.txt") as f:
        session_counter = int(f.read()) + 1 
except IOError:
    session_counter = 1

recording_counter = 0

gate = 600
audio_sample = []

rec=False
above_gate=False

while (True):
    data = stream.read(chunk)
    rms = audioop.rms(data, 2)
    print(rms)
    
    #set above gate
    if rms >= gate:
        above_gate = True
    else:
        above_gate = False
    
    if above_gate == False:
        if rec == True:
            # stop recording, write file
#            print("Recording stopped")
            UID = "LIVE" + str(session_counter).zfill(5) + "_" + str(recording_counter).zfill(5)
            audio_sample_file_path = basedir + UID + ".wav"
            write_audio_data(audio_sample, audio_sample_file_path,byterate)
            write_audio_records(basedir,session_counter,audio_sample_file_path, UID)
            result = subprocess.check_output("./kaldi_decode.sh", shell=True)
            result = result.split(" ",1)[1].strip()
            print(result)
            if len(result) >= 2:
                try:
#                    cmd = process_line(result)
#                    scan_result = scan(result)
#                    pdb.set_trace()
#                    ast = parse(scan_result)
#                    printAST(ast)
#                    execute(ast, f == sys.stdin)
#                    execute(ast, True)
                    print("-----------------")
                    print(result)
#                    print(cmd)
#                    os.system(cmd)
        
                except GrammaticalError as e:
                    print "Error:", e
                
                
            
            recording_counter +=1
            rec = False
            
    else:
        if rec == True:
            #contine recording
            #print("contine recording")
#            print(rms)
            audio_sample.append(data)
        else:
            # start recording
#            print("Recording started")
            audio_sample = []
            audio_sample.append(data)
            rec = True
            
    





















import sys
import wave
#import pyaudi  o
import audioop
import unicodedata
import time
import numpy as np
import os
import re
import subprocess
import pdb
from datetime import datetime
import time

from silvius.process_line import process_line

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
# write_audio_file function

def write_log(basedir,UID, transc, cmd, decode_duration, audio_sample_file_path):
    
    outputfile=open(basedir + 'log','a')
    
    time_stamp = str(datetime.now())
    
    outputfile.write(time_stamp + "," + UID + "," + transc + "," + cmd + "," + decode_duration + "," + audio_sample_file_path + "\n")
    
    

#----------------------------------------------------------------------------
# open stream

mic = -1
chunk = 0
byterate = 16000
#pa = pyaudio.PyAudio()
sample_rate = byterate
stream = None

debug=False
listen_mode = False


basedir= "decode/data/"

voco_data_base = "/home/bartek/Projects/ASR/voco_data/"


#allow listen and debug mode
try:
    options = sys.argv
    
    for x in options:
        if x == "listen":
            listen_mode = True
            print("listen_mode = True")
        if x == "debug":
            debug = True
            print("debug = True")

except:
    print("")


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

    
#create skp2gender
outputfile=open(basedir + 'spk2gender','w')
outputfile.write("bartek m \n")

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
    
    
#    print(rms)
    
    #set above gate
    if rms >= gate:
        above_gate = True
    else:
        above_gate = False
    
    if above_gate == False:
        if rec == True:
            
            # stop recording, write file
#            print("Recording stopped")

            decoding_start = time.time()
    
            UID = "LIVE" + str(session_counter).zfill(8) + "_" + str(recording_counter).zfill(5)
    
            audio_sample_file_path = basedir + UID + ".wav"
        
            write_audio_data(audio_sample, audio_sample_file_path,byterate)
            write_audio_records(basedir,session_counter,audio_sample_file_path, UID)
            
            result = subprocess.check_output("./kaldi_decode.sh", shell=True)
            result = result.split(" ",1)[1].strip()
            
            decoding_end = time.time()
            
            if len(result) >= 2:
                try:
                    
                    print("-----------------")
                    print(result)
                    cmd = process_line(result)
                    print(cmd)
                    
                    if not listen_mode:
                        os.system(cmd)
        
                    decode_duration = decoding_end - decoding_start
            
                    write_log(basedir,UID,result,cmd,decode_duration,audio_sample_file_path)
                    
                except:
                    print "Error"
                    write_log()
                
                
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
            
    





















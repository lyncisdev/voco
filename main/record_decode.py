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
from datetime import datetime
import time
import traceback
import pprint
from silvius.process_line import process_line

#----------------------------------------------------------------------------
# write_audio_file function
#----------------------------------------------------------------------------


def write_audio_data(audio_sample, audio_sample_file_path, byterate):

    new_audio_sample = []
    rms = []

    # calculate RMS of each point
    for x in audio_sample:
        rms.append(audioop.rms(x, 2))

    # calculate scaling factor
    sample_mean = np.mean(rms)
    scaling_factor = 4000 / sample_mean

    # multiply samples by scaling factor
    for x in audio_sample:
        new_audio_sample.append(audioop.mul(x, 2, scaling_factor))

    # Write audio file
    audio_sample_file = open(audio_sample_file_path, 'w+')

    w = wave.open(audio_sample_file_path, "w")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(byterate)

    for x in new_audio_sample:
        w.writeframes(x)

    w.close()


#----------------------------------------------------------------------------
# write_audio_file function
#----------------------------------------------------------------------------


def write_audio_records(basedir, session_counter, audio_sample_file_path, UID):

    # Write sample files - should these not be permanent?

    outputfile = open(basedir + 'wav_sample.scp', 'w')
    outputfile.write(UID + " " + audio_sample_file_path + "\n")

    outputfile = open(basedir + 'utt2spk_sample', 'w')
    outputfile.write(UID + " bartek" + "\n")

    outputfile = open(basedir + 'spk2utt_sample', 'w')
    outputfile.write("bartek " + UID + "\n")

    outputfile = open(basedir + 'wav.scp', 'a')
    outputfile.write(UID + " " + audio_sample_file_path + "\n")

    outputfile = open(basedir + 'utt2spk', 'a')
    outputfile.write(UID + " bartek" + "\n")

    outputfile = open(basedir + 'spk2utt', 'a')
    outputfile.write("bartek " + UID + "\n")

    with open("session_counter.txt", "w") as f:
        f.write(str(session_counter))


#----------------------------------------------------------------------------
# write_log function
#----------------------------------------------------------------------------


def write_log(basedir, UID, transc, cmd, decode_duration,
              audio_sample_file_path):

    outputfile = open(basedir + 'log', 'a')

    time_stamp = str(datetime.now())

    outputfile.write(time_stamp + "," + UID + "," + transc + "," + cmd + "," +
                     decode_duration + "," + audio_sample_file_path + "\n")


#----------------------------------------------------------------------------
# Main Loop
#----------------------------------------------------------------------------

mic = -1
chunk = 0
byterate = 16000
pa = pyaudio.PyAudio()
sample_rate = byterate
stream = None

debug = False
noexec_mode = False
playback_mode = False

voco_data_base = "/home/bartek/Projects/ASR/voco_data/"

# ln -sv ~/Projects/ASR/voco_data/staging/ ~/Projects/ASR/voco/voco_main/decode/data

basedir = voco_data_base + "staging/"

#----------------------------------------------------------------------------
# Parse input options - noexec, debug, playback
#----------------------------------------------------------------------------

try:
    options = sys.argv

    for x in options:
        if x == "noexec":
            noexec_mode = True
            print("noexec_mode = True")
        if x == "debug":
            debug = True
            print("debug = True")
        if x == "playback":
            playback_mode = True
            print("playback_mode = True")
        if x == "help":
            print("noexec, debug, playback")
except:
    print("Input argument error")

#----------------------------------------------------------------------------
# set_up mic
#------------------------------------------------------------------------

try:
    chunk = 3 * 512 * 2 * sample_rate / byterate

    if mic == -1:
        mic = pa.get_default_input_device_info()['index']
        if debug:
            print("Selecting default mic")
            print("Using mic " + str(mic))

    stream = pa.open(
        rate=sample_rate,
        format=pyaudio.paInt16,
        channels=1,
        input=True,
        input_device_index=mic,
        frames_per_buffer=chunk)

    pp = pprint.PrettyPrinter(depth=3, width=5)
    pp.pprint(pa.get_default_input_device_info())

except IOError, e:
    if (e.errno == -9997 or e.errno == 'Invalid sample rate'):
        new_sample_rate = int(
            pa.get_device_info_by_index(mic)['defaultSampleRate'])
        if (sample_rate != new_sample_rate):
            sample_rate = new_sample_rate

    print >> sys.stderr, "\n", e
    print >> sys.stderr, "\nCould not open microphone. Please try a different device."
    global fatal_error
    fatal_error = True
    sys.exit(0)

    print >> sys.stderr, "\nLISTENING TO MICROPHONE"
    last_state = None

#----------------------------------------------------------------------------
# create skp2gender - only needs to be created once
#----------------------------------------------------------------------------
outputfile = open(basedir + 'spk2gender', 'w')
outputfile.write("bartek m \n")

#----------------------------------------------------------------------------
# Setup session and recording counter
#----------------------------------------------------------------------------

try:
    with open("session_counter.txt") as f:
        session_counter = int(f.read()) + 1
except IOError:
    session_counter = 1

recording_counter = 0
audio_sample = []
rec = False
prev_sample = ""
timeout = 0

#----------------------------------------------------------------------------
# Benchmark noise floor
#----------------------------------------------------------------------------

rms = 0
for i in range(0, 10):
    data = stream.read(chunk)

    tmp_rms = audioop.rms(data, 2)

    rms += tmp_rms

    if debug:
        print(tmp_rms)

avg_rms = rms / 10.0
gate = 1.4 * avg_rms
end_gate = 1.2 * avg_rms

print("Noise floor: " + str(avg_rms))
print("Start recording gate: " + str(gate))
print("Stop recording gate: " + str(end_gate))

# gate = 800
# end_gate = 600

os.system("aplay media/shovel.wav")

#----------------------------------------------------------------------------
# start recording
#----------------------------------------------------------------------------

while (True):
    data = stream.read(chunk)
    rms = audioop.rms(data, 2)

    # if debug:
    #     print(rms)

    if rec == False:
        if rms >= gate:
            audio_sample = []
            audio_sample.append(prev_sample)
            audio_sample.append(data)
            rec = True
            timeout = 0

    else:
        if rms >= end_gate:
            audio_sample.append(data)
        elif (rms < end_gate) and (timeout < 2):
            audio_sample.append(data)
            timeout += 1
        else:
            # stop recording, write file

            UID = "LIVE" + str(session_counter).zfill(8) + "_" + str(
                recording_counter).zfill(5)

            audio_sample_file_path = basedir + UID + ".wav"

            duration_dict = {}
            time_start = time.time()

            write_audio_data(audio_sample, audio_sample_file_path, byterate)
            write_audio_records(basedir, session_counter,
                                audio_sample_file_path, UID)

            time_end = time.time()
            time_duration = time_end - time_start
            duration_dict['write_files'] = time_duration
            time_start = time_end

            result = subprocess.check_output("./kaldi_decode.sh", shell=True)
            result = result.split(" ", 1)[1].strip()

            if debug:
                print(result)

            time_end = time.time()
            time_duration = time_end - time_start
            duration_dict['decode'] = time_duration
            time_start = time_end

            if len(result) == 0:
                # os.system("aplay media/micro.wav")
                print("Error: result")
            else:
                try:

                    cmd = process_line(result)
                    time_end = time.time()
                    time_duration = time_end - time_start
                    duration_dict['process'] = time_duration
                    time_start = time_end

                    if len(cmd) == 0:
                        # os.system("aplay media/micro.wav")

                        print("Error")
                    else:
                        print(cmd)

                    if not noexec_mode:
                        subprocess.Popen([cmd], shell=True)

                    time_end = time.time()
                    time_duration = time_end - time_start
                    duration_dict['execute'] = time_duration
                    duration_dict['total'] = duration_dict[
                        'write_files'] + duration_dict[
                            'decode'] + duration_dict[
                                'process'] + duration_dict['execute']

                    if debug:
                        print("-----------------")
                        print(result + "\n")
                        print(duration_dict['total'])

                    if playback_mode:
                        os.system("aplay " + audio_sample_file_path)

                    write_log(basedir, UID, result, cmd,
                              str(duration_dict['total']),
                              audio_sample_file_path)
                    if debug:
                        print("Wrote log to:" + basedir + "log")

                except Exception as e:
                    # os.system("aplay media/micro.wav")
                    print(e)
                    tb = traceback.format_exc()
                    print(tb)

            recording_counter += 1
            rec = False

    prev_sample = data

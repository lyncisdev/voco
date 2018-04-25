#!/usr/bin/python

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

import select


# loopback
# pactl load-module module-loopback latency_msec=1
# pactl unload-module module-loopback

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
    outputfile.close()

    outputfile = open(basedir + 'utt2spk_sample', 'w')
    outputfile.write(UID + " bartek" + "\n")
    outputfile.close()

    outputfile = open(basedir + 'spk2utt_sample', 'w')
    outputfile.write("bartek " + UID + "\n")
    outputfile.close()

    outputfile = open(basedir + 'wav.scp', 'a')
    outputfile.write(UID + " " + audio_sample_file_path + "\n")
    outputfile.close()

    outputfile = open(basedir + 'utt2spk', 'a')
    outputfile.write(UID + " bartek" + "\n")
    outputfile.close()

    outputfile = open(basedir + 'spk2utt', 'a')
    outputfile.write("bartek " + UID + "\n")
    outputfile.close()

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
debug = False
noexec_mode = False
playback_mode = False
literal_mode = False

pp = pprint.PrettyPrinter(depth=4, width=5)


i3blocks_text_filename = "i3blocks_text.txt"
i3blocks_color_filename = "i3blocks_color.txt"

i3blocks_color_dict = {'rec': "#FF0000", 'decoding': "#FFAE00", 'transc':"#FFFFFF"}



try:
    voco_data_base = os.environ['VOCO_DATA']
    print(os.environ['VOCO_DATA'])
except:
    print('VOCO_DATA not defined')

# voco_data_base = "/home/bartek/Projects/ASR/voco_data/"

# ln -sv ~/Projects/ASR/voco_data/staging/ ~/Projects/ASR/voco/voco_main/decode/data

basedir = voco_data_base + "/staging/"

#----------------------------------------------------------------------------
# Parse input options - noexec, debug, playback, literal
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
        if x == "literal":
            literal_mode = True
            print("literal_mode = True")
        if x == "help":
            print("noexec, debug, playback")
except:
    print("Input argument error")

#----------------------------------------------------------------------------
# set_up mic
#------------------------------------------------------------------------

try:

    mic = -1
    chunk = 0
    byterate = 16000
    pa = pyaudio.PyAudio()
    sample_rate = byterate
    stream = None
    chunk = 128 * 2 * sample_rate / byterate

    if mic == -1:

        mic_info = pa.get_default_input_device_info()

        mic = mic_info['index']

        pp.pprint(mic_info)

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

    if debug:
        pp = pprint.PrettyPrinter(depth=3, width=5)
        pp.pprint(pa.get_default_input_device_info())

except IOError as e:
    if (e.errno == -9997 or e.errno == 'Invalid sample rate'):
        new_sample_rate = int(
            pa.get_device_info_by_index(mic)['defaultSampleRate'])
        if (sample_rate != new_sample_rate):
            sample_rate = new_sample_rate

    print(sys.stderr, "\nCould not open microphone. Please try a different device.")
    sys.exit(0)

print("\nLISTENING TO MICROPHONE")
last_state = None



#----------------------------------------------------------------------------
# create skp2gender - only needs to be created once
#----------------------------------------------------------------------------
outputfile = open(basedir + "audio_records/" + 'spk2gender', 'w')
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

avg_rms = 400
gate = 800
end_gate = 400

print("Noise floor: " + str(avg_rms))
print("Start recording gate: " + str(gate))
print("Stop recording gate: " + str(end_gate))

#----------------------------------------------------------------------------
# Notify user
#----------------------------------------------------------------------------

# os.system("aplay media/shovel.wav")

#----------------------------------------------------------------------------
# Speech test
#----------------------------------------------------------------------------

speechtest = True

count = 0

if speechtest:
    while (True):

        data = stream.read(chunk)
        rms = audioop.rms(data, 2)

        print("%0.2f - %0.2f - %i" % (stream.get_input_latency(),stream.get_cpu_load(),rms))


        if debug:
            print(rms)

        if rec == False:
            if rms >= gate:
                print("\nStarting recording - %i" % rms)
                rec = True
                timeout = 0
                audio_sample.append(prev_sample)
                audio_sample.append(data)
            # else:
                # print("Not recording - %i" % rms)


        else:
            if rms >= end_gate:
                # print("Continuing - %i" % rms)
                audio_sample.append(data)
                timeout = 0

            elif (rms < end_gate) and (timeout < 10):
                # print("Ending - %i" % rms)
                audio_sample.append(data)
                timeout += 1
            else:
                # stop recording, write file

                filename = "tmp" + str(count) + ".wav"
                write_audio_data(audio_sample, filename, byterate)
                os.system("aplay " + filename)


                from scipy import fft
                import matplotlib.pyplot as plt
                # other usual libraries 

                S = np.fromstring(''.join(audio_sample), dtype=np.int16)
                N = np.size(S)
                K = 64
                Step = 4
                wind =  0.5*(1 -np.cos(np.array(range(K))*2*np.pi/(K-1) ))
                ffts = []

                print(np.shape(S))
                print(np.shape(wind))

                # S = data_hollow['collection_hollow'][0]
                Spectogram = []
                for j in range(int(Step*N/K)-Step):

                    # print("%i - %i - %i" % (j, int(j * K/Step),int((j+Step) * K/Step)))

                    vec = S[int(j * K/Step) : int((j+Step) * K/Step)] * wind
                    Spectogram.append(abs(fft(vec,K)[:int(K/2)]))


                Spectogram=np.asarray(Spectogram)
                print(np.shape(Spectogram))
                plt.imshow(Spectogram.T,aspect='auto',origin='auto',cmap='spring')
                plt.axis('off')

                # raw_input("...")

                # import matplotlib.pyplot as plt
                # from scipy import signal
                # from scipy.io import wavfile

                # sample_rate, samples = wavfile.read(filename)
                # # samples = np.fromstring(''.join(audio_sample), dtype=np.int16)

                # frequencies, times, spectogram = signal.spectrogram(samples, sample_rate,mode='psd')

                # plt.pcolormesh(times, frequencies, spectogram)
                # plt.imshow(spectogram)
                # plt.ylabel('Frequency [Hz] - %i' % sample_rate)
                # plt.xlabel('Time [sec]')


                plt.savefig("tmp" + str(count) + ".jpg")



                count += 1

                rec = False
                audio_sample = []
                print("Done\n")

        prev_sample = data



#----------------------------------------------------------------------------
# start recording
#----------------------------------------------------------------------------

DICTATE_FLAG = False
PAUSE_FLAG = False

while (True):
    data = stream.read(chunk)
    rms = audioop.rms(data, 2)


    if debug:
        print(rms)



    if select.select([sys.stdin,],[],[],0.0)[0]:
        line = sys.stdin.readline()
        if line.strip() == "p":
            PAUSE_FLAG = not PAUSE_FLAG
            print("PAUSE FLAG: %s" % PAUSE_FLAG)


    if rec == False:
        if rms >= gate:

            i3blocks_text = open(i3blocks_text_filename,"w")
            i3blocks_text.write("REC\n\n%s\n" % i3blocks_color_dict['rec'])
            i3blocks_text.close()
            subprocess.Popen(["pkill", "-RTMIN+12", "i3blocks"])

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

            i3blocks_text = open(i3blocks_text_filename,"w")
            i3blocks_text.write("DECODING\n\n%s\n" % i3blocks_color_dict['decoding'])
            i3blocks_text.close()
            subprocess.Popen(["pkill", "-RTMIN+12", "i3blocks"])


            UID = "LIVE" + str(session_counter).zfill(8) + "_" + str(
                recording_counter).zfill(5)

            audio_sample_file_path = basedir + "audio_data/" + UID + ".wav"

            duration_dict = {}
            time_start = time.time()

            write_audio_data(audio_sample, audio_sample_file_path, byterate)
            write_audio_records(basedir + "audio_records/", session_counter,
                                audio_sample_file_path, UID)

            time_end = time.time()
            time_duration = time_end - time_start
            duration_dict['write_files'] = time_duration
            time_start = time_end

            # if not DICTATE_FLAG:

            result = subprocess.check_output("./kaldi_decode.sh")
            result = result.split(" ", 1)[1].strip()

            # else:
            #     # pass audio to ASPIRE and reset dictate_flag
            #     result = subprocess.check_output("./aspire_decode.sh", shell=True)
            #     print(result)
            #     DICTATE_FLAG = False
            #     print("DECODE_FLAG has been set")

            if debug:
                print(result)

            time_end = time.time()
            time_duration = time_end - time_start
            duration_dict['decode'] = time_duration
            time_start = time_end

            if len(result) == 0:
                if debug:
                    print("Zero length command")

                    i3blocks_text = open(i3blocks_text_filename,"w")
                    i3blocks_text.write("NONE\n\n%s\n" % i3blocks_color_dict['decoding'])
                    i3blocks_text.close()
                    subprocess.Popen(["pkill", "-RTMIN+12", "i3blocks"])


            else:
                try:

                    if not literal_mode:
                        cmd = process_line(result)
                    else:
                        cmd = process_line(result,"LITERALMODE")


                    if cmd == "DICTATE_FLAG":
                        DICTATE_FLAG = True
                        cmd = ""

                    time_end = time.time()
                    time_duration = time_end - time_start
                    duration_dict['process'] = time_duration
                    time_start = time_end

                    print(result)
                    print(cmd)
                    print("")

                    if not noexec_mode and not PAUSE_FLAG:
                        subprocess.Popen([cmd], shell=True)

                    i3blocks_text = open(i3blocks_text_filename,"w")
                    i3blocks_text.write("%s\n\n%s\n" % (result.upper(),i3blocks_color_dict['transc']))
                    i3blocks_text.close()
                    subprocess.Popen(["pkill", "-RTMIN+12", "i3blocks"])

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
                    print(e)
                    tb = traceback.format_exc()
                    print(tb)

            recording_counter += 1
            rec = False

    prev_sample = data

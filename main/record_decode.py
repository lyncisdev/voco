#!/usr/bin/python3

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
# import pdb
from datetime import datetime
import time
import traceback
import pprint
# from silvius.process_line import process_line
import collections
import select
from parser import parser, implementation

# Note:
# adding a loopback listening interface to pulseaudio
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
# write i3 blocks
#----------------------------------------------------------------------------


def write_i3blocks(msg, color):

    i3blocks_text_filename = "i3blocks_text.txt"
    i3blocks_color_dict = {
        'recording': "#FF0000",
        'decoding': "#FFAE00",
        'neutral': "#FFFFFF"
    }

    i3blocks_text = open(i3blocks_text_filename, "w")
    i3blocks_text.write("%s\n\n%s\n" % (msg, i3blocks_color_dict[color]))
    i3blocks_text.close()
    subprocess.Popen(["pkill", "-RTMIN+12", "i3blocks"])


#----------------------------------------------------------------------------
# Global variables
#----------------------------------------------------------------------------
XDO_TOOL = '/usr/bin/xdotool '

#----------------------------------------------------------------------------
# Main Loop
#----------------------------------------------------------------------------


def main():

    debug = False
    noexec_mode = False
    playback_mode = False
    literal_mode = False

    pp = pprint.PrettyPrinter(depth=4, width=60)

    try:
        voco_data_base = os.environ['VOCO_DATA']
        print(os.environ['VOCO_DATA'])
    except:
        print('VOCO_DATA not defined')

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
        chunk = 128 * 2 * sample_rate // byterate

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

        print(sys.stderr,
              "\nCould not open microphone. Please try a different device.")
        sys.exit(0)

    print("\nLISTENING TO MICROPHONE")

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
    audio_samples = collections.deque()
    audio_frames_prefix = 10
    audio_timeout_frames = 20

    rec = False
    timeout = 0

    #----------------------------------------------------------------------------
    # Benchmark noise floor
    #----------------------------------------------------------------------------

    gate = 800
    end_gate = 800

    print("Start recording gate: " + str(gate))
    print("Stop recording gate: " + str(end_gate))

    #----------------------------------------------------------------------------
    # Notify user
    #----------------------------------------------------------------------------

    # os.system("aplay media/shovel.wav")

    #----------------------------------------------------------------------------
    # init parser
    #----------------------------------------------------------------------------

    dynamic_rules, static_rules, var_lookup = parser.init()

    #----------------------------------------------------------------------------
    # start recording
    #----------------------------------------------------------------------------

    DICTATE_FLAG = False
    PAUSE_FLAG = False

    while (True):

        sample = stream.read(chunk)
        rms = audioop.rms(sample, 2)
        audio_samples.append(sample)

        if rec == False:
            if rms >= gate:

                write_i3blocks('REC', 'recording')

                rec = True
                timeout = 0

            else:
                while len(audio_samples) > audio_frames_prefix:
                    audio_samples.popleft()

        else:
            if rms >= end_gate:
                timeout = 0
            elif (rms < end_gate) and (timeout < audio_timeout_frames):
                timeout += 1
            else:
                # stop recording, write file

                #----------------------------------------------------------------------------
                # Get window context
                #----------------------------------------------------------------------------

                active_window = subprocess.check_output(
                    ['/usr/bin/xdotool', 'getactivewindow'])
                active_window = active_window.strip().decode('UTF-8')
                windowclass = subprocess.check_output(
                    ["xprop", "-notype", "-id", active_window, "WM_CLASS"])
                windowclass = windowclass.strip().decode('UTF-8')
                expr = "WM_CLASS = \"([^\"]*)\", \"([^\"]*)\""
                m = re.search(expr, windowclass)
                context = m.group(2).upper()

                write_i3blocks('DECODING', 'decoding')

                UID = "LIVE" + str(session_counter).zfill(8) + "_" + str(
                    recording_counter).zfill(5)

                audio_sample_file_path = basedir + "audio_data/" + UID + ".wav"

                # Write the WAV file and the Kaldi records
                write_audio_data(audio_samples, audio_sample_file_path,
                                 byterate)
                write_audio_records(basedir + "audio_records/",
                                    session_counter, audio_sample_file_path,
                                    UID)

                # Run the Kaldi script
                result = subprocess.check_output(
                    "./kaldi_decode.sh").strip().decode('UTF-8')

                try:
                    result = result.split(" ", 1)[1].strip()
                except IndexError as e:
                    result = ""

                if debug:
                    print(UID)
                    print(result)

                if len(result) == 0:
                    if debug:
                        print("Zero length command")

                    write_i3blocks('NONE', 'neutral')

                else:
                    try:

                        # Replay the audio clip
                        if playback_mode:
                            os.system("aplay " + audio_sample_file_path)

                        commands, matches = parser.parsephrase(
                            dynamic_rules, static_rules, var_lookup, result,
                            context)

                        # Execute the command
                        if not noexec_mode and not PAUSE_FLAG:

                            for cmd in commands:

                                if cmd[0] == "/usr/bin/xdotool":
                                    subprocess.call(cmd)
                                else:
                                    subprocess.Popen(
                                        cmd,
                                        shell=False,
                                        stdin=None,
                                        stdout=None,
                                        stderr=None,
                                        close_fds=True)


                        write_i3blocks(result.upper(), 'neutral')
                        write_log(basedir, UID, result, "", "0.0",
                                  audio_sample_file_path)

                        print("%s |  %s" % (result, context))

                        if debug:
                            print("-----------------")
                            print(result + "\n")
                            print("Wrote log to:" + basedir + "log")

                    except Exception as e:
                        print(e)
                        tb = traceback.format_exc()
                        print(tb)

                recording_counter += 1
                rec = False


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nShutting down\n')
        write_i3blocks("", 'neutral')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

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
from datetime import datetime
import time
import traceback
import pprint
import collections
import select
from parser import parser, implementation

# Note:
# adding a loopback listening interface to pulseaudio
# pactl load-module module-loopback latency_msec=1
# pactl unload-module module-loopback


def write_audio_data(audio_sample, audio_sample_file_path, byterate):
    '''
    This function writes out the WAV file to disk
    TODO: update scaling factors
    '''

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
# This function writes out the audio records required by Kaldi to perform transcription.
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
# This function rights of the supporting file required by i3 blocks. I3 blocks is a GUI element of i3wm tiling window manager.
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
# XDO_TOOL is the application that executes the keystrokes given to it by the parser.
# It also provides other convenient functions such as getting the window context (the currently selected window)
# from the window manager and switching between windows.
#----------------------------------------------------------------------------
XDO_TOOL = '/usr/bin/xdotool '

#----------------------------------------------------------------------------
# Main Loop
# The main four loop performs 5 major functions.
# 1. process any audio received by the microphone and determine if the user speaking
# 2. if speech is detected record the speech until the speaking stops
# 3. save the audio and call Kaldi to transcribe the recorded speech
# 4. Pass the transcribed speech to the parser and receive back an array of commands to execute
# 5. Execute the required commands by calling subprocess
#----------------------------------------------------------------------------


def main():
    pp = pprint.PrettyPrinter(depth=4, width=60)


    # VOCO_DATA is the environment variable that points to where VOCO saves audio data and records
    try:
        voco_data_base = os.environ['VOCO_DATA']
        print(os.environ['VOCO_DATA'])
    except:
        print('VOCO_DATA not defined')

    basedir = voco_data_base + "/staging/"

    #----------------------------------------------------------------------------
    # Parse input options - noexec, debug, playback
    # noexec - don't execute any commands, useful for debugging
    # debug - show additional debugging information during runtime
    # playback - playback the audio recorded
    #----------------------------------------------------------------------------

    debug = False
    noexec_mode = False
    playback_mode = False


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
    # set_up pyaudio
    # important to note here is that the chunk size affects the latency, so smaller chunk size is better
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

        sys.exit(0)

    print("\nLISTENING TO MICROPHONE")

    #----------------------------------------------------------------------------
    # create skp2gender - only needs to be created once
    #----------------------------------------------------------------------------
    outputfile = open(basedir + "audio_records/" + 'spk2gender', 'w')
    outputfile.write("bartek m \n")

    #----------------------------------------------------------------------------
    # Setup session and recording counter
    # the session and recording counters are combined to form a unique identifier ( called UID in Kaldi) for example
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
    # setup gates
    # these two variables set the sound levels (RMS) the recorded signal 
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
    # Load the static and dynamic rules from file
    #----------------------------------------------------------------------------

    dynamic_rules, static_rules, var_lookup = parser.init()

    #----------------------------------------------------------------------------
    # start recording
    # Begin the main loop
    #----------------------------------------------------------------------------


    while (True):

        # read the sample, calculated its RMS and appended to the queue
        sample = stream.read(chunk)
        rms = audioop.rms(sample, 2)
        audio_samples.append(sample)

        if rec == False:
            if rms >= gate:

                # notify the user the system has started recording
                write_i3blocks('REC', 'recording')

                rec = True
                timeout = 0

            else:
                # if the system is not recording trim the queue to only keep a few historic samples.
                # This is so that when speech is detected the system has some initial samples of the signal, which helps in decoding.
                while len(audio_samples) > audio_frames_prefix:
                    audio_samples.popleft()

        else:
            if rms >= end_gate:
                timeout = 0
            elif (rms < end_gate) and (timeout < audio_timeout_frames):
                timeout += 1
            else:
                # Stop recording transcribe the audio and execute the commands

                #----------------------------------------------------------------------------
                # Get window context
                # this function gets the class of window that is currently selected, for example Firefox or Emacs
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

                # notify the user decoding has started
                write_i3blocks('DECODING', 'decoding')

                # create the UID
                UID = "LIVE" + str(session_counter).zfill(8) + "_" + str(
                    recording_counter).zfill(5)

                audio_sample_file_path = basedir + "audio_data/" + UID + ".wav"

                # Write the WAV file and the Kaldi records
                write_audio_data(audio_samples, audio_sample_file_path,
                                 byterate)

                write_audio_records(basedir + "audio_records/",
                                    session_counter, audio_sample_file_path,
                                    UID)

                # Run Kaldi, the script decodes for your sample and saves the transcription to a text file.
                result = subprocess.check_output(
                    "./kaldi_decode.sh").strip().decode('UTF-8')

                try:
                    result = result.split(" ", 1)[1].strip()
                except IndexError as e:
                    # this error occurs if Kaldi did not manage to transcribe anything
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
                        # Replay the audio clip if playback mode is on
                        if playback_mode:
                            os.system("aplay " + audio_sample_file_path)

                        # parse the transcription
                        commands, matches = parser.parsephrase(
                            dynamic_rules, static_rules, var_lookup, result,
                            context)

                        # Execute the command
                        if not noexec_mode:
                            for cmd in commands:

                                # if the command requires XDOTOOL then use subprocess.call
                                # since that waits for each command to complete before the next commander started.
                                # This is usefull for commands where order is important such as keystrokes since
                                # it prevents them being executed in the wrong order.
                                # Otherwise use pop open since this prevents VOCO locking up while waiting for the command to complete.
                                # For instance in Emacs if you issue a command to helm this command will not complete until Helm is closed
                                # and this will prevent VOCO decoding any further commands.

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

                        # show the user what the Kaldi transcribed
                        write_i3blocks(result.upper(), 'neutral')

                        # write the log
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

        # clean up when the user issues the control+c command

        print('\nShutting down\n')
        write_i3blocks("", 'neutral')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

from listener import Listener
from recogniser import GoogleRecognizer, KaldiRecognizer
from parser import CommandParser
from implementer import Implementer
from notifier import Notifier
from contextmanager import ContextManager
from executor import DefaultExecutor
from inputmanager import InputManager

import time
import wave
import os
import copy

XDO_TOOL = '/usr/bin/xdotool'


class Manager():
    def run(self):
        pass


class KaldiManager(Manager):
    def __init__(self):
        self.listener = Listener()
        self.listener.init_microphone()

        self.state = 0
        self.speech_frames = list()

        self.recognizer = KaldiRecognizer()

        self.contextmanager = ContextManager()

        self.parser = CommandParser()

        self.implementer = Implementer()
        self.contextmanager = ContextManager()
        self.notifier = Notifier()
        self.executor = DefaultExecutor()
        # self.inputmanager = InputManager()
        # self.inputmanager.register()

        self.XDO_TOOL = '/usr/bin/xdotool '

        # VOCO_DATA is the environment variable that points to where VOCO saves audio data and records
        try:
            self.voco_data_base = os.environ['VOCO_DATA']
            print(os.environ['VOCO_DATA'])
        except:
            print('VOCO_DATA not defined')

        self.basedir = self.voco_data_base + "/staging/"

        # self.debug = True
        self.debug = False

        if self.debug:
            print(self.voco_data_base)
            print(self.basedir)

        # create skp2gender - only needs to be created once

        if not os.path.exists(self.basedir + "audio_records/"):
            os.makedirs(self.basedir + "audio_records/")

        outputfile = open(self.basedir + "audio_records/" + 'spk2gender', 'w')

        outputfile.write("bartek m \n")

        try:
            with open("session_counter.txt") as f:
                self.session_counter = int(f.read()) + 1
        except IOError:
            self.session_counter = 1

        self.recording_counter = 0

    def chunk_stream_start(self):
        pass

    def chunk_stream_end(self):

        total_duration = 0.0
        for frame in self.speech_frames:
            total_duration += frame[4]

        # print("Duration: %0.2f" % total_duration)

        if total_duration > 0.3:

            # create the UID
            UID = "LIVE" + str(self.session_counter).zfill(8) + "_" + str(
                self.recording_counter).zfill(5)

            audio_sample_file_path = self.basedir + "audio_data/" + UID + ".wav"

            if self.debug:
                print(UID)
                print(audio_sample_file_path)

            outputfile = open(
                self.basedir + "audio_records/" + 'wav_sample.scp', 'w')
            outputfile.write(UID + " " + audio_sample_file_path + "\n")
            outputfile.close()

            outputfile = open(
                self.basedir + "audio_records/" + 'utt2spk_sample', 'w')
            outputfile.write(UID + " bartek" + "\n")
            outputfile.close()

            outputfile = open(
                self.basedir + "audio_records/" + 'spk2utt_sample', 'w')
            outputfile.write("bartek " + UID + "\n")
            outputfile.close()

            outputfile = open(self.basedir + "audio_records/" + 'wav.scp', 'a')
            outputfile.write(UID + " " + audio_sample_file_path + "\n")
            outputfile.close()

            outputfile = open(self.basedir + "audio_records/" + 'utt2spk', 'a')
            outputfile.write(UID + " bartek" + "\n")
            outputfile.close()

            outputfile = open(self.basedir + "audio_records/" + 'spk2utt', 'a')
            outputfile.write("bartek " + UID + "\n")
            outputfile.close()

            with open("session_counter.txt", "w") as tmp_file:
                tmp_file.write(str(self.session_counter))

            wav_file = wave.open(audio_sample_file_path, "w")
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.listener.FS)

            for frame in self.speech_frames:
                wav_file.writeframes(frame[5])

            wav_file.close()

            self.recording_counter += 1

            result = self.recognizer.recognize(audio_sample_file_path)

            self.notifier.notify(result, "white")

            context = self.contextmanager.getcontext()

            # parse the transcription
            commands, matches = self.parser.parse(result, context)
            # print(commands)

            self.executor.execute(commands)

    def run(self):
        while True:

            frame = self.listener.chunk_queue.get()

            speaking_counter, chunk_timestamp, chunk_type, queue_sequence, duration, chunk = frame

            if chunk_type == 0:
                self.notifier.notify("REC", "red")
                self.speech_frames = []
                self.chunk_stream_start()

            self.speech_frames.append(copy.deepcopy(frame))

            if chunk_type == 1 and queue_sequence > 2:
                pass

            if chunk_type == 2:

                self.notifier.notify("DECODING", "white")
                self.chunk_stream_end()
                self.notifier.clear()

            self.listener.chunk_queue.task_done()


if __name__ == "__main__":
    man = KaldiManager()
    man.run()

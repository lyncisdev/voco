import pyaudio
import audioop
from collections import deque
import os
import time
import math
import numpy as np
import scipy.fftpack
from scipy.io import wavfile
from scipy import signal

from datetime import datetime
import queue
import threading


class Listener():
    def init_microphone(self):

        # Microphone stream config.
        self.CHUNK = 128  # CHUNKS of bytes to read each time from mic
        self.FORMAT = pyaudio.paInt16  # 16 bit int = 2 byte
        self.CHANNELS = 1
        self.FS = 16000

        p = pyaudio.PyAudio()

        self.stream = p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.FS,
            input=True,
            frames_per_buffer=self.CHUNK)

        self.sample_window = self.CHUNK
        self.audiostream_size = 256 * self.sample_window
        self.psdstream_size = 256

        self.audiostream_counter = 0
        self.psdstream_counter = 0

        self.begin = False
        self.sample_counter = 0
        self.silence_value = 0.0
        self.speaking = False
        self.delay_counter = 0
        self.speaking_counter = 0
        self.stream_wav_file = None

        self.debug = False

        self.chunk_queue = queue.Queue(maxsize=0)
        self.queue_sequence = 0

        self.ma_size = 30
        self.FFTcut = 8
        self.mean_threshold = 2
        self.delay_counter_max = 50

        self.audiostream = np.zeros((self.audiostream_size), dtype=np.int16)
        self.psd_stream = np.zeros(
            (self.sample_window // 2 + 1, self.psdstream_size))

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()  # Start the execution

    def reset_streams(self):

        if self.speaking:

            self.push_valid_chunk(
                self.audiostream[0:self.audiostream_size // 2])

            # self.stream_wav_file.writeframes(
            #     self.audiostream[0:self.audiostream_size // 2])

        self.audiostream[0:self.audiostream_size // 2] = self.audiostream[
            self.audiostream_size // 2:]
        self.audiostream[self.audiostream_size // 2:] = 0
        self.audiostream_counter = self.audiostream_size // 2
        self.psd_stream[:, 0:self.psdstream_size //
                        2] = self.psd_stream[:, self.psdstream_size // 2:]
        self.psd_stream[:, self.psdstream_size // 2:] = 0
        self.psdstream_counter = self.psdstream_size // 2

    def update_streams(self, sample):
        def fft(data, FS):
            win = scipy.signal.get_window('hann', len(data))
            freqs, psd = scipy.signal.welch(
                data, fs=FS, window=win, noverlap=0)
            return psd

        def running_mean(x, N):
            cumsum = np.cumsum(np.insert(x, 0, 0))
            return (cumsum[N:] - cumsum[:-N]) / float(N)

        if self.audiostream_counter > (
                self.audiostream_size - self.sample_window):
            self.reset_streams()

        start = self.audiostream_counter
        end = self.audiostream_counter + self.sample_window

        np_sample = np.fromstring(sample, dtype=np.int16)
        self.audiostream[start:end] = np_sample

        self.psd_stream[:, self.psdstream_counter] = fft(np_sample, self.FS)

        cut_PSD = self.psd_stream[self.FFTcut:, self.psdstream_counter - self.
                                  ma_size:self.psdstream_counter]
        sum_PSD = np.sum(cut_PSD, axis=0)
        log_PSD = np.log(sum_PSD)
        zmean_PSD = log_PSD - self.silence_value
        self.sample_mean = np.average(zmean_PSD)
        self.audiostream_counter += self.sample_window
        self.psdstream_counter += 1

    def calc_silence_value(self):

        silencestream = self.audiostream[0:self.audiostream_counter]
        silencepsd = self.psd_stream[:, 0:self.psdstream_counter]
        tmp_PSD = np.sum(silencepsd[self.FFTcut:, :], axis=0)
        tmp_PSD = np.log(tmp_PSD)
        self.silence_value = np.average(tmp_PSD)

    def push_valid_chunk(self, chunk, chunk_type=1):

        # queue structure
        frame = [
            self.speaking_counter, datetime.now().time(), chunk_type,
            self.queue_sequence, chunk.size / self.FS, chunk
        ]

        self.chunk_queue.put(frame)

        self.queue_sequence += 1
        if self.debug:
            print(self.chunk_queue.qsize())

    def process_sample(self):

        sample = self.stream.read(self.CHUNK)
        self.sample_counter += self.sample_window

        if self.sample_counter > self.FS and self.begin == False:

            self.calc_silence_value()

            # use smaller chunks for recording and larger to estimate initial silence
            self.audiostream_size = 64 * self.sample_window
            self.psdstream_size = 64

            self.audiostream = np.zeros(
                (self.audiostream_size), dtype=np.int16)
            self.psd_stream = np.zeros(
                (self.sample_window // 2 + 1, self.psdstream_size))

            self.audiostream_counter = 0
            self.psdstream_counter = 0

            self.begin = True
            print("BEGIN")

        self.update_streams(sample)

        if self.begin:
            if self.sample_mean > self.mean_threshold:

                self.delay_counter = self.delay_counter_max

                if self.debug:
                    print("SPEAKING: %i" % self.delay_counter)

                if not self.speaking:
                    self.speaking = True
                    self.speaking_counter += 1

                    self.queue_sequence = 0

                    self.push_valid_chunk(
                        self.audiostream[0:self.audiostream_size // 2], 0)

                    # self.stream_wav_file = wave.open(
                    #     "stream_%i.wav" % self.speaking_counter, "w")
                    # self.stream_wav_file.setnchannels(1)
                    # self.stream_wav_file.setsampwidth(2)
                    # self.stream_wav_file.setframerate(self.FS)

                    # self.stream_wav_file.writeframes(
                    #     self.audiostream[0:self.audiostream_size // 2])

            else:
                if self.speaking:
                    if self.delay_counter > 0:
                        # os.system('clear')  # on linux / os x

                        if self.debug:
                            print("SPEAKING: %i" % self.delay_counter)
                        self.delay_counter -= 1
                    else:
                        # self.stream_wav_file.writeframes(
                        #     self.audiostream[0:self.audiostream_size])

                        self.push_valid_chunk(
                            self.audiostream[self.audiostream_size // 2:self.
                                             audiostream_counter], 2)

                        # self.stream_wav_file.close()

                        # self.stream_wav_file = None

                        self.speaking = False

                else:
                    pass
                    # os.system('clear')  # on linux / os x

    def run(self):
        while True:
            self.process_sample()

    def stop(self):
        self.stream.terminate()
        # shut down stream
        pass


if __name__ == "__main__":

    listener = Listener()

    listener.init_microphone()

    time.sleep(3)
    print(listener.chunk_queue.qsize())
    time.sleep(2)
    print(listener.chunk_queue.qsize())

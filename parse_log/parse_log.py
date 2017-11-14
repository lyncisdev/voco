import re
import random
import subprocess
import pprint
import shutil
import os

voco_data_base = "/home/bartek/Projects/ASR/voco_data/"
audio_data_directory = voco_data_base + "audio_data/"
audio_records_directory = voco_data_base + "audio_records/"

# 2017-10-25 22:02:47.259551,
# LIVE00000062_00000,
# hotel,
# /usr/bin/xdotool key h,
# 0.190190076828,
# /home/bartek/Projects/ASR/voco_data/staging/LIVE00000062_00000.wav

try:
    with open("parse_counter.txt") as f:
        parse_counter = int(f.read())
except IOError:
    parse_counter = 0

try:
    with open(audio_records_directory + "naming_list_counter.txt") as f:
        naming_list_counter = int(f.read())
except IOError:
    naming_list_counter = 0

# shutil.copy2("log","log.backup")

log_file = open('error_log', 'r')
log = log_file.readlines()
log = log[parse_counter:]

log_file.close()

for x in log:
    parts = re.split(r',', x.strip())

    time_stamp = parts[0]
    UID = parts[1]
    phrase = parts[2]
    cmd = parts[3]
    decode_duration = parts[4]
    audio_sample_file_path = parts[5]

    # if phrase.find("eight") != -1:
    #     phrase = phrase.replace("eight","space")
    if True:
        print("---------------------------")
        print(UID + "\n")
        print(audio_sample_file_path + "\n")
        print("")
        print(phrase + "\n\n")

        processed = False
        while not processed:
            os.system("aplay " + audio_sample_file_path)

            accept = raw_input("accept?")
            if accept == "n":
                with open("error_log", "a") as f:
                    f.write(x)
                print("Rejected!")
                processed = True
            elif accept == "r":
                processed = False
            else:

                shutil.move(audio_sample_file_path,
                            audio_data_directory + UID + ".wav")

                outputfile = open(audio_records_directory + 'wav.scp', 'a')
                outputfile.write(UID + " " + audio_sample_file_path + "\n")

                outputfile = open(audio_records_directory + "text", 'a')
                outputfile.write(UID + " " + phrase + "\n")

                outputfile = open(audio_records_directory + 'utt2spk', 'a')
                outputfile.write(UID + " bartek" + "\n")
                naming_list_counter += 1
                with open(audio_records_directory + "naming_list_counter.txt",
                          "w") as f:
                    f.write(str(naming_list_counter))

                print("accepted")
                processed = True

    parse_counter += 1
    with open("parse_counter.txt", "w") as f:
        f.write(str(parse_counter))

print("")
print("recording list completed!")

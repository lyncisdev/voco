import re
import random
import subprocess
import pprint
import shutil
import os

# voco_data_base = "/home/bartek/Projects/ASR/voco_data/"

voco_data_base = "/home/lyncis/proj/voco/data/"
audio_data_directory = voco_data_base + "audio_data/"
audio_records_directory = voco_data_base + "audio_records/"

ROOT = ["/home/bartek/Projects/ASR", "/home/bartek/Projects/ASR/"]

#----------------------------------------------------------------------------
# Open Parse Counter
#----------------------------------------------------------------------------
try:
    with open("parse_counter.txt") as f:
        parse_counter = int(f.read())
except IOError:
    parse_counter = 0

#----------------------------------------------------------------------------
# Open Naming List Counter
#----------------------------------------------------------------------------
try:
    with open(audio_records_directory + "naming_list_counter.txt") as f:
        naming_list_counter = int(f.read())
except IOError:
    naming_list_counter = 0

#----------------------------------------------------------------------------
# Backup Log File
#----------------------------------------------------------------------------

shutil.copy2("log", "log.backup")

#----------------------------------------------------------------------------
# Iterate over log file
#----------------------------------------------------------------------------

log_file = open('log', 'r')
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
        print("%d - %d\n" % (parse_counter, len(log)))
        # print(audio_sample_file_path + "\n")
        print("")
        print(phrase + "\n\n")

        processed = False
        while not processed:

            # os.system("aplay " + audio_sample_file_path)

            os.system("aplay " + audio_sample_file_path)

            accept = raw_input("\naccept (enter) / replay (r) / reject (n)?")

            if accept == "n":
                with open("error_log", "a") as f:
                    f.write(x)
                print("-------> Rejected!")
                processed = True

            elif accept == "r":
                processed = False
                print("-------> Replay")

            else:
                shutil.move(
                    audio_sample_file_path,
                    audio_data_directory + UID + ".wav")

                outputfile = open(audio_records_directory + 'wav.scp', 'a')
                outputfile.write(UID + " " + audio_data_directory + UID
                                 + ".wav" + "\n")

                outputfile = open(audio_records_directory + "text", 'a')
                outputfile.write(UID + " " + phrase + "\n")

                outputfile = open(audio_records_directory + 'utt2spk', 'a')
                outputfile.write(UID + " bartek" + "\n")

                naming_list_counter += 1

                with open(audio_records_directory + "naming_list_counter.txt",
                          "w") as f:
                    f.write(str(naming_list_counter))

                print("-------> Accepted")
                processed = True

    parse_counter += 1
    with open("parse_counter.txt", "w") as f:
        f.write(str(parse_counter))

print("")
print("recording list completed!")

#
# play UID
#
#

import os

try:
    voco_data_base = os.environ['VOCO_DATA']
    print(os.environ['VOCO_DATA'])
except:
    print('VOCO_DATA not defined')



while(True):
    UID = input("UID:")

    UID_type = UID[0:3]
    print(UID_type)

    # if UID_type == "REC":
    basedir = voco_data_base
    audio_sample_file_path = basedir + "/audio_data/" + UID + ".wav"
    os.system("aplay " + audio_sample_file_path)

    # elif UID_type == "LIV":

    #     basedir = voco_data_base + "/staging/"
    #     audio_sample_file_path = basedir + "audio_data/" + UID + ".wav"
    #     os.system("aplay " + audio_sample_file_path)

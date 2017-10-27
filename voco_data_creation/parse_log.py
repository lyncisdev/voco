# this will parse the log file

log_file = open('~\Projects\ASR\voco_data\log', 'r')

#
#def write_log(basedir, UID, transc, cmd, decode_duration,
#             audio_sample_file_path):

commands = log_file.readlines()

for x in commands:

    parts = re.split(r',', x)

    phrase = parts[0]
    freq = int(parts[1])
    group = int(parts[2])

    basedir,
    UID,
    transc,
    cmd,
    decode_duration,
    audio_sample_file_path

# this will parse the log file



log_file = open('log','r')



commands = log_file.readlines()

for x in 
parts = re.split(r',', x)

    phrase = parts[0]
    freq = int(parts[1])
    group = int(parts[2])
    

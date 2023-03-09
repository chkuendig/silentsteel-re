import pprint
import json
import sys
from play_idx import play_audio, play_video 
SKIP=-1
CONTINUE=0
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

folder = "/Volumes/Untitled/"
def parse(data):
    parts = []
    string = ""
    while(len(data)>0):
        byte = data.pop(0)
        char = chr(byte)

        if(char == "{"):
            if(len(string.strip()) > 0):
                parts.append(string.strip())
            parts.append(parse(data))
            string = ""
        elif(char == "}"):       
            if(len(string.strip()) > 0):
                parts.append(string.strip())
            return parts
        else:
            string += char
    return parts

def executeCmd(cmd):
    if(cmd[0:3] == "?r$" and cmd[-1] == ";"):
        play_video(int(cmd[3:-1]))

    elif(cmd[0:2] == "?j"):
        play_video(int(cmd[2:]))
        return SKIP
    else:
        print(cmd[1:2])
        print("Unsupported command: %s"%cmd)
    return CONTINUE

def playSequence(sequence):
    cmds = sequence.split(" > ")
    print(cmds);
    for cmd in cmds:
        if(len(cmd)>0):
            ret = executeCmd(cmd)
            if(ret == SKIP):
                return 

def runExchange(exchange):
    options = {}
    lastOption = ""
    for line in exchange:
        print(line)
        if(line[0] in ["+","=","-"]):
            options[line] = []
            lastOption = line
        elif(line[0] == ">"):
            options[lastOption].append(line)
    
    print(options.keys())
    input("Press Enter to continue...")

with open(folder + "STEEL.EXE", 'rb') as fin:
    fin.seek(93805)
    data = fin.read(330130-93805)
    parts = parse(bytearray(data)[0:15000])
    exchange = -1
    skipExchange = False
    for part in parts:
        
        if(part[0].startswith("sequence")):
            skipExchange = False
            playSequence(part[0][8:])
            #input("Press Enter to continue...")
        elif isinstance(part, str) and part.endswith('EXCHANGE'):
            if not skipExchange:
                exchange = int(part[0:-9])
            else:
                print("Skipping exchange" + part)
        elif exchange >0:
            ret = runExchange(part)
            if(ret == SKIP):
                skipExchange = True
            exchange = -1
            
            
        else:
             print(bcolors.BOLD+"WARNING: "+bcolors.OKBLUE+json.dumps(part)+ bcolors.ENDC)


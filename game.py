import json
import sys
import random
from play_idx import play_audio, play_video
SKIP = -1
CONTINUE = 0


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
    while (len(data) > 0):
        byte = data.pop(0)
        char = chr(byte)

        if (char == "{"):
            if (len(string.strip()) > 0):
                parts.append(string.strip())
            parts.append(parse(data))
            string = ""
        elif (char == "}"):
            if (len(string.strip()) > 0):
                parts.append(string.strip())
            if (len(parts) == 1):
                return parts[0]
            return parts
        else:
            string += char
    return parts


def executeCmd(cmd):
    cmd_parts = cmd.split(";")

    if (len(cmd_parts) > 1 and len(cmd_parts[1].strip()) > 0):
        print("Message: %s" % cmd_parts[1])
    cmd = cmd_parts[0]
    if (cmd[0:3] == "?r$"):
        play_video(int(cmd[3:]))

    elif (cmd[0:2] == "?j"):
        play_video(int(cmd[2:]))
        return SKIP
    else:
        print("Unsupported command: %s" % cmd)

    return CONTINUE


def playSequence(sequence):
    cmds = sequence.split(">")
    print(cmds)
    for cmd in cmds:
        cmd = cmd.strip()
        if (len(cmd) > 0):
            ret = executeCmd(cmd)
            if (ret == SKIP):
                return


def runExchange(exchange):
    options = {}
    lastOption = ""
    for line in exchange:
        if (line[0] in ["+", "=", "-"]):
            options[line] = []
            lastOption = line
        elif (line[0] == ">"):
            options[lastOption].append(line)
        else:
            print("ASSSD %s" % line)
    for idx, key in enumerate(options.keys()):
        print("%i. %s" % (idx+1, key[7:]))
    choice_idx = -1
    while (choice_idx < 0 or choice_idx > 2):
        inputstr = input("Your Choice:")
        if (inputstr.isdigit()):
            choice_idx = int(inputstr)-1

    choice_str = list(options.keys())[choice_idx]
    audio_idx = choice_str[3:7]
    play_audio(int(audio_idx))

    result_str = random.choice(options[choice_str])
    cmds = result_str.split(">")
    for cmd in cmds:
        cmd = cmd.strip()
        if (len(cmd) > 0):
            ret = executeCmd(cmd)
            if (ret == SKIP):
                return SKIP


with open(folder + "STEEL.EXE", 'rb') as fin:
    fin.seek(93805)
    data = fin.read(330130-93805)
    scenes = parse(bytearray(data))
    exchange = -1
    skipExchange = False
    skip = 0
    if (len(sys.argv) >= 2 and sys.argv[1].isdigit()):
        scenes = scenes[int(sys.argv[1]):]
    for scene in scenes:
        if (isinstance(scene, str) and scene.startswith("sequence")):
            skipExchange = False
            print(scene)
            playSequence(scene[8:])
        elif isinstance(scene, str) and scene.endswith('EXCHANGE'):
            if not skipExchange:
                exchange = int(scene[0:-9])
            else:
                print("Skipping exchange" + scene)
        elif exchange > 0:
            ret = runExchange(scene)
            if (ret == SKIP):
                skipExchange = True
            exchange = -1

        elif not skipExchange:
            print(bcolors.BOLD+"UNSUPPORTED SCENE: " +
                  bcolors.OKBLUE+json.dumps(scene) + bcolors.ENDC)

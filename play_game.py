import json
import sys
import nefile
import random
from play_idx import play_audio, play_video
CONTINUE = -1
AUTOPLAY = False


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


def split_lines(data):
    parts = []
    string = ""
    while (len(data) > 0):
        char = data.pop(0)

        if (char == "{"):
            if (len(string.strip()) > 0):
                parts.append(string.strip())
            parts.append(split_lines(data))
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


def executeInstruction(instruction):
    instruction_parts = instruction.split(";")

    if (len(instruction_parts) > 1 and len(instruction_parts[1].strip()) > 0):
        print("<< %s" % instruction_parts[1].strip())
    instruction = instruction_parts[0].strip()
    if (instruction[0:3] == "?r$"):
        # print("DEBUG: Play Video - %s" % instruction)
        play_video(int(instruction[3:]))

    elif (instruction[0:2] == "?j"):
        # print("DEBUG: Jump - %s" % instruction)
        return int(instruction[2:])
    else:
        print(bcolors.BOLD+"Warning command: " +
              bcolors.OKBLUE+"%s" % instruction + bcolors.ENDC)

    return CONTINUE


def playSequence(sequence):
    instructions = sequence.strip().split(">")
    for instruction in instructions:
        instruction = instruction.strip()
        if (len(instruction) > 0):
            ret = executeInstruction(instruction)
            if (ret != CONTINUE):
                return ret
    return CONTINUE


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
            print("WARNING WRONG EXCHANGE: %s" % line)
    for idx, key in enumerate(options.keys()):
        print("%i. %s" % (idx+1, key[7:]))
    choice_idx = -1
    while (choice_idx < 0 or choice_idx > 2):
        if not AUTOPLAY:
            inputstr = input("Your Choice: ")
            if (inputstr.isdigit()):
                choice_idx = int(inputstr)-1
        else:
            choice_idx = random.randrange(3)
            print("Your Choice: %i" % (choice_idx+1))

    choice_str = list(options.keys())[choice_idx]
    print(">> %s" % choice_str[7:])
    audio_idx = choice_str[3:7]
    play_audio(int(audio_idx))

    result_str = random.choice(options[choice_str])
    instructions = result_str.split(">")
    for instruction in instructions:
        instruction = instruction.strip()
        if (len(instruction) > 0):
            ret = executeInstruction(instruction)
            if (ret != CONTINUE):
                return ret
    return CONTINUE


def playResource(resource):
    lines = split_lines(list(resource))
    exchange = -1
    for scene in lines:
        if (isinstance(scene, str) and scene.startswith("sequence")):
            ret = playSequence(scene[8:])
            if (ret != CONTINUE):
                return ret
        elif isinstance(scene, str) and scene.endswith('EXCHANGE'):
            exchange = int(scene[0:-9])
        elif exchange > 0 or (isinstance(scene, list) and scene[0][0:1] == "+"):
            ret = runExchange(scene)
            if (ret != CONTINUE):
                return ret
            exchange = -1

        else:
            print(bcolors.BOLD+"Warning Unsupported Scene: " +
                  bcolors.OKBLUE+json.dumps(scene) + bcolors.ENDC)
    return CONTINUE


steel = nefile.NE('/Volumes/Untitled/STEEL.EXE')
data_resources = steel.resource_table.resources["DATA"]
scenes = {}
for resource_id, resource in data_resources.items():
    data_str = resource.data.read().decode(
        "ascii").rstrip("\x1a \x00")  # there's padding
    scenes[resource_id] = data_str


resource_ids = list(scenes.keys())
idx = 0
sceneId = resource_ids[idx]
if (len(sys.argv) >= 2 and sys.argv[1].isdigit()):
    sceneId = int(sys.argv[1])  # jump forward to this scene/resource
    idx = resource_ids.index(sceneId)

if (len(sys.argv) >= 2 and "auto" in sys.argv):
    AUTOPLAY = True

while True:
    ret = playResource(scenes[sceneId])
    if (ret != CONTINUE):
        sceneId = ret
        idx = resource_ids.index(sceneId)
    else:
        idx += 1
        if (idx < len(resource_ids)):
            resource_ids[idx]
        else:
            print("Congratulations - you finished the Game!")
            break

import struct
import sys
import wave
from subprocess import run
folder = "/Volumes/Untitled/"


def parseIdx(filename):
    parts = {}
    lastIdx = -1
    print(filename)
    with open(filename, 'rb') as in_file:
        print("====================")
        print(filename)
        data = in_file.read(16)
        format = data[0:4].decode("ascii")
        length = int.from_bytes(data[12:14], "little")
        print("Format: %s, Length: %i" % (format, length))
        print("Full Header: %s" % data.hex())
        print("----------------------")
        i = 0
        while True:
            i += 1
            idx = in_file.read(2)
            if len(idx) == 0:                # breaks loop once no more binary data is read
                break
            idx = int.from_bytes(idx, "little")
            offset = struct.unpack('I', in_file.read(4))[0]
            if (idx > 0):
                parts[idx] = {}
                parts[idx]["start"] = offset
            if (lastIdx > 0):
                parts[lastIdx]["end"] = offset
            lastIdx = idx
        print("Parts found: i: %s len:%s" % (i, len(parts)))
        return parts


audio_params = None
with wave.open(folder+"SOUNDS1.WAV", 'rb') as wav:
    audio_params = wav.getparams()

video_parts = parseIdx(folder+"VIDEO1.IDX")
sound_parts = parseIdx(folder+"SOUNDS1.IDX")


def play_audio(idx):
    file = folder+"SOUNDS1.WAV"
    part = sound_parts[idx]
    start = part["start"]
    end = part["end"]
    length = (audio_params.nframes/audio_params.framerate)
    size = audio_params.nframes*audio_params.sampwidth*audio_params.nchannels
    bitrate = audio_params.framerate*audio_params.nchannels*audio_params.sampwidth
    # todo: this somehow isn't frame accurate (sometimes cuts off split second too early or to late)
    start_sec = start/bitrate
    end_sec = end/bitrate
    duration = end_sec-start_sec
    seek = "%.2f" % start_sec
    duration_str = "%.2f" % duration
    run(['ffplay', '-hide_banner', '-loglevel', 'warning', '-nodisp',
        '-autoexit', '-i', file, '-ss', seek, '-t', duration_str])
    return


def play_video(idx):
    file = folder+"VIDEO1.MPG"
    if (idx in video_parts):
        part = video_parts[idx]
        start = part["start"]
        end = part["end"]
        with open(file, 'rb') as fin:
            fin.seek(start)

            run(['ffplay', '-hide_banner', '-vf', 'scale=-1:480',
                 # '-vf','setpts=0.25*PTS','-af','atempo=4',        # for speedup;
                '-loglevel', 'warning', '-autoexit', '-'], input=fin.read(end - start))
    else:
        print("WARNING: Video not found %i" % idx)
    return


if (len(sys.argv) == 3 and sys.argv[1] == "v" and int(sys.argv[2])):
    play_video(int(sys.argv[2]))
elif (len(sys.argv) == 3 and sys.argv[1] == "a" and int(sys.argv[2])):
    play_audio(int(sys.argv[2]))

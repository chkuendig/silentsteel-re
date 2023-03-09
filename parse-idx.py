import struct

def parseIdx(filename): 
    parts = {}
    lastIdx = -1
    print(filename)
    with open(filename ,'rb') as in_file:
        print("====================")
        print(filename)
        data = in_file.read(16)
        format = data[0:4].decode("ascii")
        length = int.from_bytes(data[12:14], "little")
        print("Format: %s, Length: %i"%(format,length))
        print("Full Header: %s"%data.hex())
        print("----------------------")
        while True:
            idx = in_file.read(2)
            if len(idx) == 0:                # breaks loop once no more binary data is read
                break
            offset = struct.unpack( 'I',in_file.read(4))[0]
            print("%i: %i"%(int.from_bytes(idx, "little"),offset))               # I also like it all in caps. 
            idx = int.from_bytes(idx, "little")
            if(idx > 0):
                parts[idx]={}
                parts[idx]["start"] = offset
            if(lastIdx > 0):
                parts[lastIdx]["end"] = offset
            lastIdx=idx
        return parts



video_parts = parseIdx("/Volumes/Untitled/VIDEO1.IDX")



sound_parts = parseIdx("/Volumes/Untitled/SOUNDS1.IDX")

print(video_parts)
print("-----")
print(sound_parts)
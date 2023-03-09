def parse(line,pos=0,ident=0,lastPos=0):
    while(pos<len(line) ):
        ident_str = "   "*ident
        char = line[pos]
        pos+=1
        if(char == '{'):
            print(ident_str+line[lastPos:pos])
            lastPos=pos
            ident+=1
        elif(char == '}'):
            print(ident_str+line[lastPos:pos-1])
            ident-=1
            ident_str = "   "*ident
            print(ident_str+char) # unident ending of block
            lastPos=pos
   
    
with open("steel.script" ,'rb') as in_file:
    i = 0
    line = ""
    while True:
        char = in_file.read(1);
        #print(char)
        if len(char) == 0:                # breaks loop once no more binary data is read
            break
        if(char == b'\x00'):
            #i+=1
            if len(line)> 0:   
                parse(line)
                #if(i>=3):
                #    break
            line = ""
            print("NULL ")

            print("%i ---- "%i)
        elif(char == b'\x1a'):
            if len(line)> 0:   
                parse(line)
            line = ""
            print("SUB ")

            i+=1
            print("%i ---- "%i)
        else:   
            line+=char.decode("ascii")
        if i>20:
            break;



    #todo: autoplay: 
    # cat video1.1.mpg | ffplay -vf "setpts=0.25*PTS" -af "atempo=4" -autoexit -
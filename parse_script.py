import nefile

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
   
steel = nefile.NE('/Volumes/Untitled/STEEL.EXE')
data_resources = steel.resource_table.resources["DATA"]
i = 0
for resource_id, resource in data_resources.items():
    data_str = resource.data.read().decode("ascii").rstrip("\x1a \x00") # there's padding 
    print("%i: -----------------------------------------------------"%(resource_id) ) 
    parse(data_str)
    print("-----------------------------------------------------" ) 

    i+=1


    
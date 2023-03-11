# Reverse Engineering Silent Steel

Silent Steel is a 1995 submarine simulator computer game by Tsunami Games. It was created during the influx of interactive movies during the 1990s. The game is composed almost entirely of live-action full motion video, with sparse computer-generated graphics depicting external shots of the boat during torpedo attacks and atmospheric fly-bys. More about *Silent Steel* is available on [Wikipedia](https://en.wikipedia.org/wiki/Silent_Steel), [MobyGames](https://www.mobygames.com/game/7993/silent-steel/) and the [ScummVM Wiki](https://wiki.scummvm.org/index.php/Silent_Steel). 

![](cover.jpg)

This project tries to reverse engineer the data files of the game and implement a barbone interpreter in python to play the game on modern machines (it was originally released as a 16bit executable for Win 3.11) and provide a basis to reimplement the game - for example in ScummVM.

## Status: WIP !!!

First few scenes are playable, but the story still skips sometimes.

## Compatibility:

At the moment this only supports the promotional disc available at the [Internet Archive](https://archive.org/details/silentsteeldisconepromotional).

## Requirements: 

Only **Python 3**, with [nefile](https://github.com/npjg/nefile) and `ffplay` from **FFmpeg** should be required to run the game.

## Data Formats:

### Game Executable
```STEEL.EXE``` is the main game executable in 16 bit [New Executable](https://en.wikipedia.org/wiki/New_Executable) formatand contains all scripts as binary resources. This format is very well documented and there's multiple portable parsers for it. I used the [radare2 source code](https://github.com/radareorg/radare2/blob/master/libr/bin/format/ne) and [OSDEV.org Wiki](https://wiki.osdev.org/NE) for my research. 

**How to parse ```STEEL.EXE```:**

Thankfully, the format is not too complicated, so it's pretty straightforward to get to the scripts and the identifiers we need:
* The first  `0x80` (128) bytes are the DOS Stub, we can ignore this, but have to remember to add this count to some offsets later.
* The position of the resources table is encoded at byte 35 in the header (see OSDEV link above) - byte 163 in the file. 
* In our case, this byte is '00x60' or 96 in decimal. Adding this to the start of the header at 128 bytes means we now jump to byte 224.
* We can skimm over the details of the resource table, but the resources (type F4 04) we are looking for start at byte 410 and theres 85 (`\x54` in the 3rd byte) of them. The first two resources look as follows: (2nd line parsed)
    ![Resource Table](resource%20table%20(54x%2004f4%20entries).png)
    ```
    Field:  | Offset     | Size    | Attributes   | Resource Type ID
    Raw:    | CE 2D      | 06 00   | 20 10        | E9 83
    Parsed: |   01 6E 70 |  00 30  | 1020 (,Pure) |  83E9 -> 03E9 -> ID: 1001
    Raw:    | D4 2D      | 83 02   | 20 10        | EA 83
    Parsed: |   01 6E A0 |   14 18 | 1020 (,Pure) |  83EA -> 03EA -> ID: 1002        
    ```
   * **Size and Offset** need to be left shifted according to the exponent encoded at the start of the resource table. (byte 224 which is x03 in our case). FYI: the offset is relative to the start of the file, not the Windows header like most of the other offsets. Example:
       - *Size 1:* `06 00` (Little Endian/LE) 0000 0110 0000 0000, Big Endian/BE: 0000 0000  0000 0110, lshift by 3 -> 0011 0000  -> size is `00 30`
       - *Offset 1:* `CE 2D` (LE) 1100 1110 0010 1101, BE: 0010 1101 1100 1110, shift by 3: 1 0110 1110 0111 0000 -> offset is  `01 6E 70`
       - *Size 2:* `83 02` (LE), BE: x02x83, 0000 0010 1000 0011,  by 3: 0001 0100 0001 1000 _> size is `14 18`
       - *Offset 2:* `D4 2D` (LE),BE: x2DxD4, 0010 1101 1101 0100,  by 3: 1 0110 1110 1010 0000 -> offset is `01 6E A0`
    * **Resource Type ID**: This is an integer type if the high-order bit is set (8000h); otherwise, it is an offset to the type string. In our case these are always integers for the resource types we care about.

In the end and way too late, I discoverd the amazing [nefile](https://github.com/npjg/nefile) which does this all for us, and which is what I ended up using for the player.

## Additional Tools Used:
- [Ghidra](https://ghidra-sre.org/) to browse the resources and poke around a bit - didn't decompile anything really.
- [windows95 in Electron](https://github.com/felixrieseberg/windows95/) to play the game a bit (couldn't be bothered to setup a proper emulator/virtualization).
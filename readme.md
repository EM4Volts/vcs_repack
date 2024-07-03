vcspy


small python script to unpack and pack source 1's .vcs (valve compiled shader), files.
only works for vcs files of version 6 which should be modern vcs files from sfm, portal 2, titanfall2 etc.
this is mainly intended to be used for mass decompilation and recompilation for small changes in all files.

doesnt do dupe records as it seems they are not needed.
can in theory make new vcs files but really shouldnt


usage:

unpack: 

vcspy.py -u <shader_file>

pack:

vcspy.py -p <shader_folder>


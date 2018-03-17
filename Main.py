from TexReader import read_tex
from SpassWriter import SpassWriter
import os
import sys

"""
Each file passed as input has its own ceremony object sent to the writer which parses it to spass.
"""

if len(sys.argv) == 1:
    print "You have to pass the files to be parsed as parameters! Mind the extensions of the files ;)"

files = sys.argv[1:]
#files = ["ceremony1.tex", "ceremony2.tex", "ceremony3.tex", "ceremony4.tex", "ceremony5.tex"]

writer = SpassWriter()

for file_name in files:

    if os.path.splitext(file_name)[1]:
        ceremony = read_tex(file_name)
        spass_name = os.path.splitext(file_name)[0]
        # generates a SPASS file with the same name as the .tex received
        writer.write_spass("ceremony_model.dfg", ceremony, spass_name)

        # runs SPASS on terminal
        os.system('SPASS -DocProof {0}.dfg > {0}.txt'.format(spass_name))
    else:
        print "Hey!!! File " + file_name + " has no extension!"

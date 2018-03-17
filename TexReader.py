import re
from Ceremony import Ceremony

"""
read_tex: Reads a given .tex file, calls for its parser and returns the final built ceremony.
"""


def read_tex(file_name):
    if file_name:
        with open(file_name, "r") as tex:
            tex_lines = tex.readlines()

        print "\nFile: ", file_name
        parse = parse_tex(tex_lines)
        return build_ceremony(parse[0], parse[1])


"""
parse_tex: Scans through the lines of the .tex file, searching for cryptographic keys and ceremony components such as sender, receiver and message
(via regular expressions).
"""

def replace(string, lst, char):
    for item in lst: 
        string = string.replace(item, char)

    return string
 
def parse_tex(tex_lines):
    ceremony_steps = []
    keys = []

    print "\nREGULAR EXPRESSION result:"

    for line in tex_lines:
        if not line or line == "\n":
            continue

        key = line.split("$")[-1]
        if "pk" in key:
            key = replace(key, [" ", "$", ".", "\\\\", "{", "}", "(", ")", ":", "[", "]", "*", "=", ",", "_", "$", "'", "-", "\\", "\n", "\r"], "")
            keys.append("key{}".format(key))
        else:
            keys.append("")

        msg = ""
        for i in range(len(line)-1,-1,-1):
            if line[i] == "&":
                line = line[:i]
                break
            else:
                msg = line[i] + msg

        msg = replace(msg, [" ", "$", ".", "\\\\", "{", "}", "(", ")", ":", "[", "]", "*", "=", ",", "_", "$", "'", "-", "\\", "\n", "\r"], "")

        line = re.sub(r"(xrightarrow)|(textit)", '', line[5:]) #excluding number of each step
        line = re.sub(r"[\'\\\_\}\-\"]+", '', line)

        result = re.findall(r'[A-Za-z\d\+\s\,]*[^\s\$\.\&\{\}\(\)\:\[\]\*]+', line)
        result.append(msg)
        print "RESULT {}".format(result)

        ceremony_steps.append(result)

    return [keys, ceremony_steps]


"""
build_ceremony: Returns a ceremony object with all its components already set, based on the .tex parsed previously.
"""


def build_ceremony(keys, ceremony_steps):
    ceremony = Ceremony()
    ceremony.keys = keys

    for step in ceremony_steps:
        length = len(step)

        sender = step[0].lower()
        layer = step[1]

        if length == 5:
            capab = ["N"]
            att = [""]
            receiver = step[3].lower()
            message = step[4].replace(" ", "").lower()

            ceremony.add_step(sender, layer, capab, att, receiver, message)

        else:  # not known length (2 ou more attackers)
            capabs = []  # capabilities
            attackers = []
            remaining = []

            if step[length - 1] == "pk":  # if there is a key in the message
                remaining = step[2:length - 4]  # ignores key fields
                receiver = step[length - 4].lower()
                message = step[length - 3].replace(" ", "").lower()
            else:
                remaining = step[2:length - 2]
                receiver = step[length - 2].lower()
                message = step[length - 1].replace(" ", "").lower()

            for index, element in enumerate(remaining):
                if index % 2 == 0:
                    capabs.append(element)
                else:
                    attackers.append(element.lower().replace(",", ""))

            ceremony.add_step(
                sender,
                layer,
                capabs,
                attackers,
                receiver,
                message)

    ceremony.print_status()
    return ceremony

class Ceremony(object):

    """
    The Ceremony class has the intention of keeping the state of a given ceremony in terms of its components (initialized in the class constructor).
    """

    def __init__(self):
        self.peers = set()  # senders and receivers
        self.msgs = set()  # messages
        self.atts = set()  # attackers

        self.keys = []  # cryptographic keys - possible blank ("") -in order
        self.sender = []  # senders -in order
        self.layer = []  # layers -in order
        self.capab = []  # capabilities for each attacker -in order
        self.att = []  # attackers - possible blank ("") -in order
        self.receiver = []  # receivers -in order
        self.msg = []  # messages -in order

    """
    add_step: Adds the ceremony components corresponding to each step of the ceremony.
    All parameters are strings, except capabilites and attackers - which can be either strings or arrays of strings.
    In the latter case, they have to be equal in size.
    """

    def add_step(
            self,
            sender,
            layer,
            capabilites,
            attackers,
            receiver,
            message):
        self.peers.add(sender)
        self.sender.append(sender)
        self.layer.append(layer)
        self.capab.append(capabilites)
        self.att.append(attackers)
        for att in attackers:
            self.atts.add(att)
        self.receiver.append(receiver)
        self.peers.add(receiver)
        self.msg.append(message)
        self.msgs.add(message)

    """
    print_status: Simply prints all ceremony attributes.
    """

    def print_status(self):
        print "\n\nPEERS SET --------------------------------\n", self.peers
        print "\n\nMSGS SET ---------------------------------\n", self.msgs
        print "\n\nATTS SET ---------------------------------\n", self.atts

        print "\n\nKEYS -------------------------------------\n", self.keys
        print "\n\nSENDER -----------------------------------\n", self.sender
        print "\n\nLAYER ------------------------------------\n", self.layer
        print "\n\nCAPAB ------------------------------------\n", self.capab
        print "\n\nATT --------------------------------------\n", self.att
        print "\n\nRECEIVER ---------------------------------\n", self.receiver
        print "\n\nMSG --------------------------------------\n", self.msg
        print "\n\n"

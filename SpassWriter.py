class SpassWriter(object):

    """
    write_spass: Initialises all strings needed further on for the predicates and conjectures.
    It also calls methods to generate formulae for the ceremony peers and messages.
    Finally, it writes the final SPASS file, following the structure of the model received by parameter.
    """

    def write_spass(self, model, ceremony, spass_name):
        with open(model, "r") as spass_model:
            self._spass = spass_model.read()  # open the model file

        self._ceremony = ceremony
        self._init = "\n"  # ceremony elements declaration
        self._attackers_forms = "\n"  # attackers formulae
        self._peers_forms = "\n"
        self._keys_forms = "\n"
        self._knows = "\n"  # Know predicates
        self._conjectures = "\n"

        self._generate_attackers_formulae()
        self._generate_peers_formulae()
        self._generate_messages_formulae()
        self._generate_message_set_formulae()

        self._spass = self._spass.replace("%VARIABLES TODO\n", self._init)

        self._text = "".join([self._peers_forms,
                              self._attackers_forms,
                              self._keys_forms,
                              self._knows,
                              "\n\n"])
        self._generate_steps()

        self._spass = self._spass.replace(
            "%DECLARATIONS AND STEPS TODO", self._text)
        self._spass = self._spass.replace(
            "%CONJECTURES TODO", self._conjectures)

        with open(spass_name + ".dfg", "w") as spass_doc:
            spass_doc.write(self._spass)

    """
    _split_capabilities: Splits the capabilities into their elementary parts.
    For instance: Single capabilities - e.g. "E" (for Eavesdrop) - are not modified;
    Combined capabilities such as "E+B" (Eavesdrop and Block) are split into ["E","B"];
    Finally, a DY full set is split into the set of its individual capabilities: ["E", "B", "S", "I", "C", "O", "F"].
    """

    def _split_capabilities(self, capab):
        if capab == "DY":
            return ["E", "B", "S", "I", "C", "O", "F"]
        return capab.split("+")

    """
    _generate_steps: Treats the first step based on number of attackers, and then calls the _generate_remaining_steps method.
    """

    def _generate_steps(self):
        # NO ATTACKER in the first message!
        if self._ceremony.capab[0][0] == "N":
            form = 'formula(\n\t{}_N(sent({},{},{})),\nstep1).\n\n'.format(
                self._ceremony.layer[0],
                self._ceremony.sender[0],
                self._ceremony.receiver[0],
                self._ceremony.msg[0])
            previous = '\t\t{}_N(sent({},{},{})),\n'.format(
                self._ceremony.layer[0],
                self._ceremony.sender[0],
                self._ceremony.receiver[0],
                self._ceremony.msg[0])
            self._text += form

        # if the very first message has more than one attacker
        elif len(self._ceremony.att[0]) > 1:
            previous = self._generate_several_attackers_first_step()
        else:
            # method for one attacker only in first message
            previous = self._generate_one_attacker_first_step()

        # calls method for remaining steps!
        self._generate_remaining_steps(previous)

    """
    _generate_one_attacker_first_step: Sets the formulae needed for the first step with a single attacker.
    """

    def _generate_one_attacker_first_step(self):
        # only one capability: ' E' , ' S' ...
        if "+" not in self._ceremony.capab[0][0] and "DY" not in self._ceremony.capab[0][0]:
            form = 'formula(\n\t{}_{}(sent({},{},{}),{}),\nstep1).\n\n'.format(
                self._ceremony.layer[0],
                self._ceremony.capab[0][0],
                self._ceremony.sender[0],
                self._ceremony.receiver[0],
                self._ceremony.msg[0],
                self._ceremony.att[0][0])
            previous = '\t\t{}_{}(sent({},{},{}),{}),\n'.format(
                self._ceremony.layer[0],
                self._ceremony.capab[0][0],
                self._ceremony.sender[0],
                self._ceremony.receiver[0],
                self._ceremony.msg[0],
                self._ceremony.att[0][0])

        else:  # more *capabilities* than just one
            cap_set = self._split_capabilities(self._ceremony.capab[0][0])

            form = "formula(\n\tand(\n"  # needs and in the formulae
            previous = "\t\tand(\n"  # needs and in the formulae

            for capability in cap_set[:-1]:  # for each capability but the last

                form += '\t\t{}_{}(sent({},{},{}),{}),\n'.format(
                    self._ceremony.layer[0],
                    capability,
                    self._ceremony.sender[0],
                    self._ceremony.receiver[0],
                    self._ceremony.msg[0],
                    self._ceremony.att[0][0])
                previous += '\t\t\t{}_{}(sent({},{},{}),{}),\n'.format(
                    self._ceremony.layer[0],
                    capability,
                    self._ceremony.sender[0],
                    self._ceremony.receiver[0],
                    self._ceremony.msg[0],
                    self._ceremony.att[0][0])

            previous += '\t\t\t{}_{}(sent({},{},{}),{})\n\t\t),\n'.format(
                self._ceremony.layer[0], cap_set[-1],
                self._ceremony.sender[0],
                self._ceremony.receiver[0],
                self._ceremony.msg[0],
                self._ceremony.att[0][0])
            form += '\t\t{}_{}(sent({},{},{}),{})\n\t),\nstep1).\n\n'.format(
                self._ceremony.layer[0], cap_set[-1],
                self._ceremony.sender[0],
                self._ceremony.receiver[0],
                self._ceremony.msg[0],
                self._ceremony.att[0][0])

        self._text += form
        return previous

    """
    _generate_several_attackers_first_step: Sets the formulae needed for the first step with multiple attackers.
    """

    def _generate_several_attackers_first_step(self):
        form = "formula(\n\tand(\n"
        previous = "\t\tand(\n"

        for index, att in enumerate(self._ceremony.att[0]):

            # only one cap: ' E' , ' S' ...
            if len(self._ceremony.capab[0][index]) == 1:
                form += '\t\t{}_{}(sent({},{},{}),{}),\n'.format(
                    self._ceremony.layer[0],
                    self._ceremony.capab[0][index],
                    self._ceremony.sender[0],
                    self._ceremony.receiver[0],
                    self._ceremony.msg[0],
                    att)
                previous += '\t\t\t{}_{}(sent({},{},{}),{}),\n'.format(
                    self._ceremony.layer[0],
                    self._ceremony.capab[0][index],
                    self._ceremony.sender[0],
                    self._ceremony.receiver[0],
                    self._ceremony.msg[0],
                    att)

            # more capabilities than just one (DY or  E + B ...and so on and so
            # forth)
            else:
                cap_set = self._split_capabilities(
                    self._ceremony.capab[0][index])

                for capability in cap_set[:-1]:
                    form += '\t\t{}_{}(sent({},{},{}),{}),\n'.format(
                        self._ceremony.layer[0],
                        capability,
                        self._ceremony.sender[0],
                        self._ceremony.receiver[0],
                        self._ceremony.msg[0],
                        att)
                    previous += '\t\t\t{}_{}(sent({},{},{}),{}),\n'.format(
                        self._ceremony.layer[0],
                        capability,
                        self._ceremony.sender[0],
                        self._ceremony.receiver[0],
                        self._ceremony.msg[0],
                        att)

                previous += '\t\t\t{}_{}(sent({},{},{}),{})\n\t\t),\n'.format(
                    self._ceremony.layer[0], cap_set[-1],
                    self._ceremony.sender[0],
                    self._ceremony.receiver[0],
                    self._ceremony.msg[0], att)
                form += '\t\t{}_{}(sent({},{},{}),{})\n\t),\nstep1).\n\n'.format(
                    self._ceremony.layer[0], cap_set[-1],
                    self._ceremony.sender[0],
                    self._ceremony.receiver[0],
                    self._ceremony.msg[0], att)

        self._text += form
        return previous

    """
    _generate_remaining_steps: Sets the formulae needed for the second up to the last step of the ceremony.
    """

    def _generate_remaining_steps(self, previous):
        remaining_msgs = self._ceremony.msg[1:]
        index = 1

        for msg in remaining_msgs:
            form = "formula(\n\timplies(\n" + previous

            if self._ceremony.capab[index][0] == "N":  # NO ATTACKER
                form += '\t\t{}_N(sent({},{},{}))\n\t),\nstep{}).\n\n'.format(
                    self._ceremony.layer[index],
                    self._ceremony.sender[index],
                    self._ceremony.receiver[index],
                    msg,
                    str(
                        index + 1))
                previous = '\t\t{}_N(sent({},{},{})),\n'.format(
                    self._ceremony.layer[index],
                    self._ceremony.sender[index],
                    self._ceremony.receiver[index],
                    msg)

            elif len(self._ceremony.att[index]) == 1:  # ONLY ONE ATTACKER
                if len(self._ceremony.capab[index]
                       [0]) == 1:  # ONLY ONE CAPABILITY!

                    form += '\t\t{}_{}(sent({},{},{}),{})\n\t),\nstep{}).\n\n'.format(
                        self._ceremony.layer[index],
                        self._ceremony.capab[index][0],
                        self._ceremony.sender[index],
                        self._ceremony.receiver[index],
                        self._ceremony.msg[index],
                        self._ceremony.att[index][0],
                        str(
                            index + 1))
                    previous = '\t\t{}_{}(sent({},{},{}),{}),\n'.format(
                        self._ceremony.layer[index],
                        self._ceremony.capab[index][0],
                        self._ceremony.sender[index],
                        self._ceremony.receiver[index],
                        self._ceremony.msg[index],
                        self._ceremony.att[index][0])

                else:  # SEVERAL CAPABILITIES
                    form += "\t\tand(\n"
                    previous = "\t\tand(\n"

                    cap_set = self._split_capabilities(
                        self._ceremony.capab[index][0])

                    for capab in cap_set[:-
                                         1]:  # all capabilities of the list but the last one
                        form += '\t\t\t{}_{}(sent({},{},{}),{}),\n'.format(
                            self._ceremony.layer[index],
                            capab,
                            self._ceremony.sender[index],
                            self._ceremony.receiver[index],
                            msg,
                            self._ceremony.att[index][0],
                            str(
                                index + 1))
                        previous += '\t\t\t{}_{}(sent({},{},{}),{}),\n'.format(
                            self._ceremony.layer[index],
                            capab,
                            self._ceremony.sender[index],
                            self._ceremony.receiver[index],
                            msg,
                            self._ceremony.att[index][0])

                    form += '\t\t\t{}_{}(sent({},{},{}),{})\n\t\t)\n\t),\nstep{}).\n\n'.format(
                        self._ceremony.layer[index], cap_set[-1],
                        self._ceremony.sender[index],
                        self._ceremony.receiver[index],
                        msg,
                        self._ceremony.att[index][0], str(index + 1))
                    previous += '\t\t\t{}_{}(sent({},{},{}),{})\n\t\t),\n'.format(
                        self._ceremony.layer[index], cap_set[-1],
                        self._ceremony.sender[index],
                        self._ceremony.receiver[index],
                        msg,
                        self._ceremony.att[index][0])

            else:  # SEVERAL ATTACKERS
                info = self._generate_several_attackers_steps(index, form)
                form = info[0]
                previous = info[1]

            self._text += form
            index += 1

    """
    _generate_several_attackers_steps: Deals with all steps (except the first) with multiple attackers.
    """

    def _generate_several_attackers_steps(self, index, form):
        form += "\t\tand(\n"
        previous = "\t\tand(\n"

        for att_index, att in enumerate(self._ceremony.att[index]):
            cap_set = self._split_capabilities(
                self._ceremony.capab[index][att_index])

            if len(cap_set) == 1:
                form += '\t\t\t{}_{}(sent({},{},{}),{}),\n'.format(
                    self._ceremony.layer[index],
                    self._ceremony.capab[index][att_index],
                    self._ceremony.sender[index],
                    self._ceremony.receiver[index],
                    self._ceremony.msg[index],
                    att,
                    str(
                        index + 1))
                previous += '\t\t\t{}_{}(sent({},{},{}),{}),\n'.format(
                    self._ceremony.layer[index],
                    self._ceremony.capab[index][att_index],
                    self._ceremony.sender[index],
                    self._ceremony.receiver[index],
                    self._ceremony.msg[index],
                    att)

            else:  # more than one capability
                for cap in cap_set[:-1]:
                    form += '\t\t\t{}_{}(sent({},{},{}),{}),\n'.format(
                        self._ceremony.layer[index],
                        cap,
                        self._ceremony.sender[index],
                        self._ceremony.receiver[index],
                        self._ceremony.msg[index],
                        att)
                    previous += '\t\t\t{}_{}(sent({},{},{}),{}),\n'.format(
                        self._ceremony.layer[index],
                        cap,
                        self._ceremony.sender[index],
                        self._ceremony.receiver[index],
                        self._ceremony.msg[index],
                        att)

                form += '\t\t\t{}_{}(sent({},{},{}),{}),\n'.format(
                    self._ceremony.layer[index],
                    cap_set[-1],
                    self._ceremony.sender[index],
                    self._ceremony.receiver[index],
                    self._ceremony.msg[index],
                    att)
                previous += '\t\t\t{}_{}(sent({},{},{}),{}),\n'.format(
                    self._ceremony.layer[index],
                    cap_set[-1],
                    self._ceremony.sender[index],
                    self._ceremony.receiver[index],
                    self._ceremony.msg[index],
                    att)

        form = form[:-2]
        form += '\n\t\t)\n\t),\nstep{}).\n\n'.format(str(index + 1))

        previous = previous[:-2]
        previous += "\n\t\t),\n"

        return [form, previous]

    """
    _generate_messages_formulae: Handles keys and pair declarations and predicates for all messages.
    """

    def _generate_messages_formulae(self):
        for index, msg in enumerate(self._ceremony.msg):  # for each message
            encrypted = False
            pair_flag = False
            sender = self._ceremony.sender[index]
            attacker = self._ceremony.att[index]
            key = self._ceremony.keys[index]

            if not key == "":
                self._generate_key_formulae(index)
                encrypted = True

            if "," in msg:
                pair = msg.split(",")
                self._ceremony.msg[index] = "pair({0},{1})".format(
                    pair[0], pair[1])
                pair_flag = True

                if '({0},0),\n'.format(
                        pair[0]) and '({0},0),\n'.format(
                        pair[1]) not in self._init:
                    self._init += '({0},0),\n'.format(pair[0])
                    self._init += '({0},0),\n'.format(pair[1])

                if 'formula(KnowsPair({0},pair({1},{2})),agent_{0}_knows_pair_{1}_and_{2}).\n'.format(
                        sender, pair[0], pair[1]) not in self._knows:
                    self._knows += 'formula(KnowsPair({0},pair({1},{2})),agent_{0}_knows_pair_{1}_and_{2}).\n'.format(
                        sender, pair[0], pair[1])

                if len(attacker) == 1 and not attacker[0] == "":
                    if 'formula(KnowsPair({0},pair({1},{2}))'.format(
                            attacker, pair[0], pair[1], key) not in self._conjectures:
                        self._conjectures += 'formula(KnowsPair({0},pair({1},{2})),attacker_{0}_knows_pair_{1}_and_{2}).\n'.format(
                            attacker[0], pair[0], pair[1])
                elif len(attacker) > 1 and not attacker[0] == "":
                    for att in attacker:
                        if 'formula(KnowsPair({0},pair({1},{2}))'.format(
                                att, pair[0], pair[1]) not in self._conjectures:
                            self._conjectures += 'formula(KnowsPair({0},pair({1},{2})),attacker_{0}_knows_pair_{1}_and_{2}).\n'.format(
                                att, pair[0], pair[1])

            if encrypted and pair_flag:
                if 'KnowsEncr({0},encr(pair({1},{2}),{3}))'.format(
                        sender, pair[0], pair[1], key) not in self._knows:
                    self._knows += 'formula(KnowsEncr({0},encr(pair({1},{2}),{3})),agent_{0}_knows_encr_pair_{1}_and_{2}).\n'.format(
                        sender, pair[0], pair[1], key)

                if len(attacker) == 1 and not attacker[0] == "":
                    if 'formula(KnowsEncr({0},encr(pair({1},{2}),{3}))'.format(
                            attacker, pair[0], pair[1], key) not in self._conjectures:
                        self._conjectures += 'formula(KnowsEncr({0},encr(pair({1},{2}),{3})),attacker_{0}_knows_encr_pair_{1}_and_{2}).\n'.format(
                            attacker[0], pair[0], pair[1], key)
                elif len(attacker) > 1 and not attacker[0] == "":
                    for att in attacker:
                        if 'formula(KnowsEncr({0},encr(pair({1},{2}),{3}))'.format(
                                att, pair[0], pair[1], key) not in self._conjectures:
                            self._conjectures += 'formula(KnowsEncr({0},encr(pair({1},{2}),{3})),attacker_{0}_knows_encr_pair_{1}_and_{2}).\n'.format(
                                att, pair[0], pair[1], key)

            if encrypted and not pair_flag:
                if 'KnowsEncr({0},encr({1},{2}))'.format(
                        sender, msg, key) not in self._knows:
                    self._knows += 'formula(KnowsEncr({0},encr({1},{2})),agent_{0}_knows_encr_{1}_and_{2}).\n'.format(
                        sender, msg, key)

                if len(attacker) == 1 and not attacker[0] == "":
                    if 'formula(KnowsEncr({0},encr({1},{2}))'.format(
                            attacker, msg, key) not in self._conjectures:
                        self._conjectures += 'formula(KnowsEncr({0},encr({1},{2})),attacker_{0}_knows_encr_{1}_and_{2}).\n'.format(
                            attacker[0], msg, key)
                elif len(attacker) > 1 and not attacker[0] == "":
                    for att in attacker:
                        if 'formula(KnowsEncr({0},encr({1},{2}))'.format(
                                att, msg, key) not in self._conjectures:
                            self._conjectures += 'formula(KnowsEncr({0},encr({1},{2})),attacker_{0}_knows_encr_{1}_and_{2}).\n'.format(
                                att, msg, key)

            if not encrypted and not pair_flag:
                if '({0},0),\n'.format(msg) not in self._init:
                    self._init += '({0},0),\n'.format(msg)

                if 'formula(Knows({0},{1})'.format(
                        sender, msg) not in self._knows:
                    self._knows += 'formula(Knows({0},{1}),agent_{0}_knows_{1}).\n'.format(
                        sender, msg)

                if len(attacker) == 1 and not attacker[0] == "":
                    if 'formula(Knows({0},{1})'.format(
                            attacker, msg) not in self._conjectures:
                        self._conjectures += 'formula(Knows({0},{1}),attacker_{0}_knows_{1}).\n'.format(
                            attacker[0], msg)
                elif len(attacker) > 1 and not attacker[0] == "":
                    for att in attacker:
                        if 'formula(Knows({0},{1})'.format(
                                att, msg) not in self._conjectures:
                            self._conjectures += 'formula(Knows({0},{1}),attacker_{0}_knows_{1}).\n'.format(
                                att, msg)

    """
    _generate_key_formulae: Sets the declarations and needed predicates for all cryptographic keys.
    """

    def _generate_key_formulae(self, index):
        if '({},0),\n'.format(self._ceremony.keys[index]) not in self._init:
            # adds declaration for key as a variable
            self._init += '({},0),\n'.format(self._ceremony.keys[index])

        if 'Key({0}),key_{0}'.format(
                self._ceremony.keys[index]) not in self._keys_forms:
            # adds Key predicate
            self._keys_forms += 'formula(Key({0}),key_{0}).\n'.format(
                self._ceremony.keys[index])

    """
    _generate_attackers_formulae: Sets the declarations and needed predicates for all attackers.
    """

    def _generate_attackers_formulae(self):
        for att in self._ceremony.atts:
            if (att != ""):
                if not "({0},0),".format(att) in self._init:
                    # attackers declaration as a variable
                    self._init += "({0},0),\n".format(att)

                if not 'formula(Attacker({0}),attacker_{0}).\n'.format(
                        att) in self._attackers_forms:
                    # Attacker predicate
                    self._attackers_forms += 'formula(Attacker({0}),attacker_{0}).\n'.format(
                        att)

                if att == "dy" and not 'formula(DY({0}),DY_{0}).\n'.format(
                        att) in self._attackers_forms:
                    self._attackers_forms += 'formula(DY({0}),DY_{0}).\n'.format(
                        att)

                elif "da" in att and not 'formula(DA({0}),DA_{0}).\n'.format(att) in self._attackers_forms:
                    self._attackers_forms += 'formula(DA({0}),DA_{0}).\n'.format(
                        att)

                elif "ma" in att and not 'formula(MA({0}),MA_{0}).\n'.format(att) in self._attackers_forms:
                    self._attackers_forms += 'formula(MA({0}),MA_{0}).\n'.format(
                        att)

    """
    _generate_peers_formulae: Sets the declarations and needed predicates for all ceremony peers (senders and receivers).
    """

    def _generate_peers_formulae(self):
        for peer in self._ceremony.peers:  # CONSIDERING THAT NO AGENT IS ALSO AN ATTACKER!!!!!!!!!!!!!
            if not "({0},0),".format(peer) in self._init:
                # all peers with no repetition are declared in spass
                self._init += '({},0),\n'.format(peer)

            if not 'formula(Agent({0}),agent_{0}).\n'.format(
                    peer) in self._peers_forms:
                # peers are agents (with no repetition)
                self._peers_forms += 'formula(Agent({0}),agent_{0}).\n'.format(
                    peer)
                # all peers are honest
                self._peers_forms += 'formula(Honest({0}),honest_{0}).\n'.format(
                    peer)

    """
    _generate_message_set_formulae: Declares all messages - with no repetition.
    """

    def _generate_message_set_formulae(self):
        for msg in self._ceremony.msgs:
            if '({},0),\n'.format(msg) not in self._init and "," not in msg:
                # message declaration as a variable
                self._init += '({},0),\n'.format(msg)

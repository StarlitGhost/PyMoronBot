# -*- coding: utf-8 -*-
"""
Created on May 04, 2014

@author: Tyranic-Moron
"""

import random

from pymoronbot.moduleinterface import ModuleInterface
from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType


class Choose(ModuleInterface):
    triggers = ['choose']
    help = 'choose <option1>, <option2>[, <optionN>] - randomly chooses one of the given options for you'

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say,
                               "You didn't give me any options to choose from! {}".format(self.help),
                               message.ReplyTo)

        if ',' in message.Parameters:
            options = message.Parameters.split(',')
        else:
            options = message.Parameters.split()

        choice = random.choice(options).strip()

        return IRCResponse(ResponseType.Say, choice, message.ReplyTo, {'chooseChoice': choice})

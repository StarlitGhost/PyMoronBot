# -*- coding: utf-8 -*-
"""
Created on May 04, 2014

@author: Tyranic-Moron
"""

import random

from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from moronbot import MoronBot


class Choose(CommandInterface):
    triggers = ['choose']
    help = 'choose <option1>, <option2>[, <optionN>] - randomly chooses one of the given options for you'

    def execute(self, message, bot):
        """
        @type message: IRCMessage
        @type bot: MoronBot
        """
        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say,
                               "You didn't give me any options to choose from! {0}".format(help),
                               message.ReplyTo)

        if ',' in message.Parameters:
            options = message.Parameters.split(',')
        else:
            options = message.Parameters.split()

        return IRCResponse(ResponseType.Say, random.choice(options).strip(), message.ReplyTo)

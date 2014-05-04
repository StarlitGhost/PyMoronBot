'''
Created on May 04, 2014

@author: Tyranic-Moron
'''

from IRCMessage import IRCMessage, IRCChannel
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface

import random

class Command(CommandInterface):
    triggers = ['choose']
    help = 'choose <option1>, <option2>[, <optionN>] - randomly chooses one of the given options for you'

    def execute(self, message=IRCMessage):
        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say,
                               "You didn't give me any options to choose from! {0}".format(help),
                               message.ReplyTo)

        if ',' in message.Parameters:
            options = message.Parameters.split(',')
        else:
            options = message.Parameters.split()

        return IRCResponse(ResponseType.Say, random.choice(options).strip(), message.ReplyTo)

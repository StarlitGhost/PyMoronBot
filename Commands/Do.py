'''
Created on Dec 20, 2011

@author: Tyranic-Moron
'''

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
from GlobalVars import *

import re

class Command(CommandInterface):
    triggers = ['do']
    help = 'do <text> - makes the bot perform the specified text'

    def execute(self, message):
        if len(message.ParameterList) > 0:
            return IRCResponse(ResponseType.Do, message.Parameters, message.ReplyTo)
        else:
            return IRCResponse(ResponseType.Do, 'Do what?', message.ReplyTo)


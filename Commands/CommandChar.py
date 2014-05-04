'''
Created on Feb 05, 2014

@author: Tyranic-Moron
'''

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
import GlobalVars

import re

class Command(CommandInterface):
    triggers = ['commandchar']
    help = "commandchar <char> - changes the prefix character for bot commands (admin-only)"

    def execute(self, message):
        if message.User.Name not in GlobalVars.admins:
            return IRCResponse(ResponseType.Say, 'Only my admins can change my command character', message.ReplyTo)

        if len(message.ParameterList) > 0:
            GlobalVars.CommandChar = message.ParameterList[0]
            return IRCResponse(ResponseType.Say, 'Command prefix char changed to \'{0}\'!'.format(GlobalVars.CommandChar), message.ReplyTo)
        else:
            return IRCResponse(ResponseType.Say, 'Change my command character to what?', message.ReplyTo)

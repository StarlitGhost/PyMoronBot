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
    triggers = ['join']
    help = 'join <channel> - makes the bot join the specified channel(s)'

    def execute(self, message):
        if len(message.ParameterList) > 0:
            responses = []
            for param in message.ParameterList:
                channel = param
                if not channel.startswith('#'):
                    channel = '#' + channel
                responses.append(IRCResponse(ResponseType.Raw, 'JOIN %s' % channel, ''))
            return responses
        else:
            return IRCResponse(ResponseType.Raw, "%s, you didn't say where I should join" % message.User.Name, message.ReplyTo)


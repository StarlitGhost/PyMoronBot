'''
Created on Dec 20, 2011

@author: Tyranic-Moron
'''

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
from GlobalVars import *

import re

class Instantiate(Function):
    Help = 'join <channel> - makes the bot join the specified channel(s)'

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('^join$', message.Command, re.IGNORECASE)
        if not match:
            return
        
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


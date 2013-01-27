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
    Help = 'do <text> - makes the bot perform the specified text'

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('^do$', message.Command, re.IGNORECASE)
        if not match:
            return
        
        if len(message.ParameterList) > 0:
            return IRCResponse(ResponseType.Do, message.Parameters, message.ReplyTo)
        else:
            return IRCResponse(ResponseType.Do, 'Do what?', message.ReplyTo)


'''
Created on Dec 20, 2011

@author: Tyranic-Moron
'''

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
import GlobalVars

import re

class Instantiate(Function):
    Help = "source - returns a link to %s's source" % GlobalVars.CurrentNick

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('^source$', message.Command, re.IGNORECASE)
        if not match:
            return
            
        return IRCResponse(ResponseType.Say, GlobalVars.source, message.ReplyTo)


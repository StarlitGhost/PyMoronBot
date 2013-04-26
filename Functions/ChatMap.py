'''
Created on Dec 20, 2011

@author: Tyranic-Moron, Emily
'''

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
from GlobalVars import *

import re

class Instantiate(Function):
    Help = 'chatmap - Responds with a link to the chatmap page. TODO: the rest of the chatmap stuff'

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('^chatmap$', message.Command, re.IGNORECASE)
        if not match:
            return
        
        return IRCResponse(ResponseType.Say,
                           'The Wonderful World of #desertbus People! http://www.tsukiakariusagi.net/chatmap.php',
                           message.ReplyTo)

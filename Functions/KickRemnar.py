'''
Created on Dec 18, 2011

@author: Tyranic-Moron
'''

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
from GlobalVars import *

import re

class Instantiate(Function):
    Help = 'Guards against the terrible influx of Mormon Jesus'

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
            
        match = re.search('([^a-zA-Z]|^)mormon jesus([^a-zA-Z]|$)',
                          message.MessageString,
                          re.IGNORECASE)
        if match and message.User.Name == 'remnar':
            return IRCResponse(ResponseType.Raw,
                               'KICK %s remnar ::I' % message.ReplyTo,
                               '')
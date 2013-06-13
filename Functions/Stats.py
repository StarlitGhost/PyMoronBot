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
    Help = 'stats - Responds with a link to the chat stats webpage(s)'

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('^stats$', message.Command, re.IGNORECASE)
        if not match:
            return
        
                           #'sss: http://www.moronic-works.co.uk/ | pisg: http://silver.amazon.fooproject.net/pisg/desertbus.html | pisg2: http://pisg.michael-wheeler.org/desertbus.html'
        return IRCResponse(ResponseType.Say,
                           'sss: http://www.moronic-works.co.uk/ | pisg: http://pisg.michael-wheeler.org/desertbus.html',
                           message.ReplyTo)

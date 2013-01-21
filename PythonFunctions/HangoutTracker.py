'''
Created on Dec 13, 2011

@author: Tyranic-Moron
'''

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
from GlobalVars import *

import re
import time

class Instantiate(Function):
    Help = 'Keeps track of the last posted G+ hangout link'

    lastCode = None
    lastDate = None
    lastUser = None
    
    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
            
        match = re.search('^hangout$', message.Command, re.IGNORECASE)
        if match:
            if self.lastCode is None:
                return IRCResponse(ResponseType.Say,
                                   'No hangouts posted yet',
                                   message.ReplyTo)
            
            return IRCResponse(ResponseType.Say,
                               'Last hangout posted: https://talkgadget.google.com/hangouts/%s (at %s by %s)' % (self.lastCode,
                                                                                                                 self.lastDate,
                                                                                                                 self.lastUser),
                               message.ReplyTo)
        
        match = re.search('(https?\://)?(talkgadget|plus)\.google\.com/hangouts/(?P<code>(extras/talk\.google\.com/)?[^\?\s]+)',
                          message.MessageString,
                          re.IGNORECASE)
        
        if not match:
            return
        
        if match.group('code') == self.lastCode:
            return
        
        self.lastCode = match.group('code')
        self.lastUser = message.User.Name
        self.lastDate = time.strftime('%X %x %Z')
        return

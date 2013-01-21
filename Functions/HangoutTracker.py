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

class data:
    lastCode = None
    lastDate = None
    lastUser = None

class Instantiate(Function):
    Help = 'hangout - gives you the last posted G+ hangout link'

    hangoutDict = {}
    
    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
            
        if message.MessageString[:1] == '|':
            match = re.search('^hangout$', message.Command, re.IGNORECASE)
            if match:
                if message.ReplyTo not in self.hangoutDict:
                    self.hangoutDict[message.ReplyTo] = None
                if self.hangoutDict[message.ReplyTo] is None:
                    return IRCResponse(ResponseType.Say,
                                       'No hangouts posted here yet',
                                       message.ReplyTo)
                
                return IRCResponse(ResponseType.Say,
                                   'Last hangout posted: https://talkgadget.google.com/hangouts/%s (at %s by %s)' % (self.hangoutDict[message.ReplyTo].lastCode,
                                                                                                                     self.hangoutDict[message.ReplyTo].lastDate,
                                                                                                                     self.hangoutDict[message.ReplyTo].lastUser),
                                   message.ReplyTo)
        
        match = re.search('(https?\://)?(talkgadget|plus)\.google\.com/hangouts/(?P<code>(extras/talk\.google\.com/)?[^\?\s]+)',
                          message.MessageString,
                          re.IGNORECASE)
        
        if not match:
            return
        
        self.hangoutDict[message.ReplyTo] = data()
        
        if match.group('code') == self.hangoutDict[message.ReplyTo].lastCode:
            return
        
        self.hangoutDict[message.ReplyTo].lastCode = match.group('code')
        self.hangoutDict[message.ReplyTo].lastUser = message.User.Name
        self.hangoutDict[message.ReplyTo].lastDate = time.strftime('%X %x %Z')
        return


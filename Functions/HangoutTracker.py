'''
Created on Dec 13, 2011

@author: Tyranic-Moron
'''

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
from GlobalVars import *

import re
import datetime

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
            
        if message.Type == 'JOIN':
            if message.User.Name in ['Emily[iOS]']
        
        match = re.search('^hango+?u?t$', message.Command, re.IGNORECASE)
        # If \hangouts is called or Emily[iOS] joins the Channel, Trigger Output.
        if (match or ((message.Type == 'JOIN') and (message.User.Name == 'Emily[iOS]'))):
            if message.ReplyTo not in self.hangoutDict:
                self.hangoutDict[message.ReplyTo] = None
            if self.hangoutDict[message.ReplyTo] is None:
                return IRCResponse(ResponseType.Say,
                                   'No hangouts posted here yet',
                                   message.ReplyTo)

            hangout = self.hangoutDict[message.ReplyTo]
            
            timeDiff = datetime.datetime.utcnow() - hangout.lastDate
            url = 'https://talkgadget.google.com/hangouts/{0}'.format(hangout.lastCode)
            byLine = 'first posted {0} ago'.format(self.strfdelta(timeDiff, '{days} day(s) {hours} hour(s) {minutes} minute(s)'))
            
            response = 'Last hangout posted: {0} ({1})'.format(url, byLine)
            
            return IRCResponse(ResponseType.Say, response, message.ReplyTo)
        
        
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
        self.hangoutDict[message.ReplyTo].lastDate = datetime.datetime.utcnow()
        return

    def strfdelta(self, tdelta, fmt):
        d = {"days": tdelta.days}
        d["hours"], rem = divmod(tdelta.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)
        return fmt.format(**d)


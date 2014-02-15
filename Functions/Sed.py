'''
Created on Feb 14, 2014

@author: Tyranic-Moron
'''

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
from GlobalVars import *

import re

# matches a sed-style regex pattern (taken from https://github.com/mossblaser/BeardBot/blob/master/modules/sed.py)
# I stripped the unnecessary escapes by using a raw string instead
sedRegex = re.compile(r"s/(?P<search>(\\\\|(\\[^\\])|[^\\/])+)/(?P<replace>(\\\\|(\\[^\\])|[^\\/])*)((/(?P<flags>.*))?)")

class Instantiate(Function):
    Help = 'matches sed-like regex replacement patterns and attempts to execute them on the latest matching line from the last 10\n'\
            'eg: s/some/all/'

    messages = []
    unmodifiedMessages = []

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = sedRegex.match(message.MessageString)

        if match:
            search = match.group('search')
            replace = match.group('replace')
            flags = match.group('flags')
            if flags is None:
                flags = ''

            response = self.substitute(search, replace, flags)

            if response is not None:
                return IRCResponse(ResponseType.Say, response, message.ReplyTo)

        else:
            self.storeMessage(message.MessageString)

    def substitute(self, search, replace, flags):
        messages = self.unmodifiedMessages if 'o' in flags else self.messages

        for message in reversed(messages):
            if 'g' in flags:
                count = 0
            else:
                count = 1

            new = re.sub(search, replace, message, count)

            if new != message:
                self.storeMessage(new, False)
                return new

    def storeMessage(self, message, unmodified=True):
        self.messages.append(message)
        self.messages = self.messages[-10:]

        if unmodified:
            self.unmodifiedMessages.append(message)
            self.unmodifiedMessages = self.unmodifiedMessages[-10:]

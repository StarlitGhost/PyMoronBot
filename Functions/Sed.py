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
sedRegex = re.compile(r"[sS]/(?P<search>(\\\\|(\\[^\\])|[^\\/])+)/(?P<replace>(\\\\|(\\[^\\])|[^\\/])*)((/(?P<flags>.*))?)")

class Instantiate(Function):
    Help = 's/search/replacement/flags - matches sed-like regex replacement patterns and attempts to execute them on the latest matching line from the last 10\n'\
            'flags are g (global), i (case-insensitive), o (only user messages), v (verbose, ignores whitespace)\n'\
            'Example usage: "I\'d eat some tacos" -> s/some/all the/ -> "I\'d eat all the tacos"'

    messages = []
    unmodifiedMessages = []

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG' and message.Type != 'ACTION':
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
                responseType = ResponseType.Say
                if response.Type == 'ACTION':
                    responseType = ResponseType.Do

                return IRCResponse(responseType, response.MessageString, message.ReplyTo)

        else:
            self.storeMessage(message)

    def substitute(self, search, replace, flags):
        messages = self.unmodifiedMessages if 'o' in flags else self.messages

        for message in reversed(messages):
            if 'g' in flags:
                count = 0
            else:
                count = 1
            
            subFlags = 0
            if 'i' in flags:
                subFlags |= re.IGNORECASE
            if 'v' in flags:
                subFlags |= re.VERBOSE

            new = re.sub(search, replace, message.MessageString, count, subFlags)

            new = new[:300]

            if new != message.MessageString:
                newMessage = message
                newMessage.MessageString = new
                self.storeMessage(newMessage, False)
                return newMessage

        return None

    def storeMessage(self, message, unmodified=True):
        self.messages.append(message)
        self.messages = self.messages[-10:]

        if unmodified:
            self.unmodifiedMessages.append(message)
            self.unmodifiedMessages = self.unmodifiedMessages[-10:]

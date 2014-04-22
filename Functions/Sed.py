'''
Created on Feb 14, 2014

@author: Tyranic-Moron
'''

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
from GlobalVars import *

import re, copy


class Instantiate(Function):
    Help = 's/search/replacement/flags - matches sed-like regex replacement patterns and attempts to execute them on the latest matching line from the last 10\n'\
            'flags are g (global), i (case-insensitive), o (only user messages), v (verbose, ignores whitespace)\n'\
            'Example usage: "I\'d eat some tacos" -> s/some/all the/ -> "I\'d eat all the tacos"'

    messages = []
    unmodifiedMessages = []

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG' and message.Type != 'ACTION':
            return
        
        match = self.match(message.MessageString)

        if match:
            search, replace, flags = match
            response = self.substitute(search, replace, flags)

            if response is not None:
                responseType = ResponseType.Say
                if response.Type == 'ACTION':
                    responseType = ResponseType.Do

                return IRCResponse(responseType, response.MessageString, message.ReplyTo)

        else:
            self.storeMessage(message)

    def match(self, message):
        """Returns (search, replace, flags) if message is a replacement pattern, otherwise None"""
        if not message.startswith('s/'):
            return
        parts = re.split(r'(?<!\\)/', message)
        if len(parts) not in (3,4):
            return
        search, replace = parts[1:3]
        if len(parts) == 4:
            flags = parts[3]
        else:
            flags = ''
        return search, replace, flags

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
                newMessage = copy.deepcopy(message)
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

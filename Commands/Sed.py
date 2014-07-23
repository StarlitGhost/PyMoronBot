# -*- coding: utf-8 -*-
"""
Created on Feb 14, 2014

@author: Tyranic-Moron
"""

import copy
import re

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface


class Sed(CommandInterface):
    triggers = ['sed']
    acceptedTypes = ['PRIVMSG', 'ACTION']
    help = 's/search/replacement/flags - matches sed-like regex replacement patterns and attempts to execute them on the latest matching line from the last 10\n'\
           'flags are g (global), i (case-insensitive), o (only user messages), v (verbose, ignores whitespace)\n'\
           'Example usage: "I\'d eat some tacos" -> s/some/all the/ -> "I\'d eat all the tacos"'

    historySize = 20

    def onLoad(self):
        #TODO: make these per-channel
        self.messages = []
        self.unmodifiedMessages = []

    def shouldExecute(self, message):
        """
        @type message: IRCMessage
        """
        if message.Type in self.acceptedTypes:
            return True

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if message.Command.lower() == 'sed':
            match = self.match(message.Parameters)
        else:
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
                return IRCResponse(ResponseType.Say, "No text matching '{0}' found in the last {1} messages".format(search, self.historySize), message.ReplyTo)

        else:
            self.storeMessage(message)

    @classmethod
    def match(cls, message):
        """Returns (search, replace, flags) if message is a replacement pattern, otherwise None"""
        if not (message.startswith('s/') or message.startswith('S/')):
            return
        parts = re.split(r'(?<!\\)/', message)
        if len(parts) not in (3, 4):
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
                newMessage = copy.copy(message)
                newMessage.MessageString = new
                self.storeMessage(newMessage, False)
                return newMessage

        return None

    def storeMessage(self, message, unmodified=True):
        self.messages.append(message)
        self.messages = self.messages[-self.historySize:]

        if unmodified:
            self.unmodifiedMessages.append(message)
            self.unmodifiedMessages = self.unmodifiedMessages[-self.historySize:]

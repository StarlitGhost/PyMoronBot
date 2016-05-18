# -*- coding: utf-8 -*-
"""
Created on Feb 17, 2015

@author: Tyranic-Moron
"""

import re

from pyxdameraulevenshtein import normalized_damerau_levenshtein_distance as ndld

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface


class AsterFix(CommandInterface):
    triggers = ['asterfix']
    acceptedTypes = ['PRIVMSG', 'ACTION']

    help = '**<fix> - looks for similar text in your last message and attempts to replace the most likely candidate'

    def onLoad(self):
        self.messages = {}

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
        if message.Command.lower() in self.triggers:
            messageString = message.Parameters
        else:
            messageString = message.MessageString

        changeMatch = re.match(r"^(?P<change>(\*\*[^\s*]+)|([^\s*]+)\*\*)$", messageString)
        if changeMatch:
            change = changeMatch.group('change').strip('*')
        else:
            self.storeMessage(message)
            return

        lastMessage = self.messages[message.User.Name]
        lastMessageList = lastMessage.MessageList
        
        # Skip 1-word messages, as it just leads to direct repetition
        if len(lastMessageList) <= 1:
            return
        
        likelyChanges = self._getCloseMatches(change, lastMessageList, 5, 0.5)
        likelyChanges = filter((lambda word: word != change), likelyChanges)

        if likelyChanges:
            target = likelyChanges[0]
            responseList = [change if word == target else word for word in lastMessageList]
            response = " ".join(responseList)
            
            # Store the modified message so it can be aster-fixed again
            self.messages[message.User.Name].MessageList = responseList

            if lastMessage.Type == 'ACTION':
                responseType = ResponseType.Do
            else:
                responseType = ResponseType.Say

            return IRCResponse(responseType, response, message.ReplyTo)

    def storeMessage(self, message):
        self.messages[message.User.Name] = message

    def _getCloseMatches(self, change, messageList, n, threshold):
        similarities = sorted([(ndld(change, part), part) for part in messageList])
        closeMatches = [word for (diff, word) in similarities if diff <= threshold]
        topN = closeMatches[:n]
        return topN

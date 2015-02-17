# -*- coding: utf-8 -*-
"""
Created on Feb 17, 2015

@author: Tyranic-Moron
"""

import difflib
import re

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse
from CommandInterface import CommandInterface


class AsterFix(CommandInterface):
    triggers = ['asterfix']
    acceptedTypes = ['PRIVMSG', 'ACTION']

    help = '*<fix> - looks for similar text in your last message and attempts to replace the most likely candidate'

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

        changeMatch = re.match(r"^\*(?P<change>[^\s*]+)$", messageString)
        if changeMatch:
            change = changeMatch.group('change')
        else:
            self.storeMessage(message)

        lastMessage = self.messages[message.User.Name].MessageString.split()
        likelyChanges = difflib.get_close_matches(change, lastMessage, 5, 0.5)
        likelyChanges = filter((lambda word: word != change), likelyChanges)

        if likelyChanges:
            target = likelyChanges[0]

            response = " ".join([change if word == target else word for word in lastMessage])

            return IRCResponse(lastMessage.ResponseType, response, message.ReplyTo)

    def storeMessage(self, message):
        self.messages[message.User.Name] = message

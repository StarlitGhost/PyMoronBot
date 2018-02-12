# -*- coding: utf-8 -*-
"""
Created on Dec 20, 2011

@author: Tyranic-Moron
"""

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface


class Source(CommandInterface):
    triggers = ['source']

    def help(self, _):
        """
        @type message: IRCMessage
        """
        return "source - returns a link to {0}'s source".format(self.bot.nickname)

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        return IRCResponse(ResponseType.Say, self.bot.sourceURL, message.ReplyTo)

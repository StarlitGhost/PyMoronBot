# -*- coding: utf-8 -*-
"""
Created on Dec 20, 2011

@author: Tyranic-Moron
"""

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType
from pymoronbot.modules.commandinterface import BotCommand


class Source(BotCommand):
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

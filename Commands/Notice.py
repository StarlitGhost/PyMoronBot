# -*- coding: utf-8 -*-
"""
Created on Oct 16, 2014

@author: Tyranic-Moron
"""

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface


class Notice(CommandInterface):
    triggers = ['notice']
    help = 'notice <target> <text> - makes the bot send the specified text as a notice to the specified target'

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) > 1:
            return IRCResponse(ResponseType.Notice, " ".join(message.ParameterList[1:]), message.ParameterList[0])
        else:
            return IRCResponse(ResponseType.Say, self.help, message.ReplyTo)

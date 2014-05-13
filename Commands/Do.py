# -*- coding: utf-8 -*-
"""
Created on Dec 20, 2011

@author: Tyranic-Moron
"""

from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from moronbot import MoronBot


class Do(CommandInterface):
    triggers = ['do']
    help = 'do <text> - makes the bot perform the specified text'

    def execute(self, message, bot):
        """
        @type message: IRCMessage
        @type bot: MoronBot
        """
        if len(message.ParameterList) > 0:
            return IRCResponse(ResponseType.Do, message.Parameters, message.ReplyTo)
        else:
            return IRCResponse(ResponseType.Do, 'Do what?', message.ReplyTo)

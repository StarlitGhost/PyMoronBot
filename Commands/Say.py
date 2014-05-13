# -*- coding: utf-8 -*-
"""
Created on Dec 20, 2011

@author: Tyranic-Moron
"""

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
from moronbot import MoronBot


class Say(CommandInterface):
    triggers = ['say']
    help = 'say <text> - makes the bot repeat the specified text'

    def execute(self, message, bot):
        """
        @type message: IRCMessage
        @type bot: MoronBot
        """
        if len(message.ParameterList) > 0:
            return IRCResponse(ResponseType.Say, message.Parameters, message.ReplyTo)
        else:
            return IRCResponse(ResponseType.Say, 'Say what?', message.ReplyTo)

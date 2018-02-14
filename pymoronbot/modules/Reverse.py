# -*- coding: utf-8 -*-
"""
Created on Nov 07, 2014

@author: Tyranic-Moron
"""

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType
from pymoronbot.moduleinterface import ModuleInterface


class Reverse(ModuleInterface):
    triggers = ['reverse', 'backwards']
    help = 'reverse <text> - reverses the text given to it'

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) > 0:
            return IRCResponse(ResponseType.Say, message.Parameters[::-1], message.ReplyTo)
        else:
            return IRCResponse(ResponseType.Say, 'Reverse what?', message.ReplyTo)

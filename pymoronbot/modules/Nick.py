# -*- coding: utf-8 -*-
"""
Created on Dec 20, 2011

@author: Tyranic-Moron
"""

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType
from pymoronbot.moduleinterface import ModuleInterface, admin


class Nick(ModuleInterface):
    triggers = ['nick', 'name']
    help = "nick <nick> - changes the bot's nick to the one specified"

    @admin
    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) > 0:
            return IRCResponse(ResponseType.Raw, 'NICK %s' % (message.ParameterList[0]), '')
        else:
            return IRCResponse(ResponseType.Say, 'Change my %s to what?' % message.Command, message.ReplyTo)

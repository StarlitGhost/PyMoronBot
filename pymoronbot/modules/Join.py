# -*- coding: utf-8 -*-
"""
Created on Dec 20, 2011

@author: Tyranic-Moron
"""

from pymoronbot.moduleinterface import ModuleInterface
from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType


class Join(ModuleInterface):
    triggers = ['join']
    help = 'join <channel> - makes the bot join the specified channel(s)'

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) > 0:
            responses = []
            for param in message.ParameterList:
                channel = param
                if not channel.startswith('#'):
                    channel = '#' + channel
                responses.append(IRCResponse(ResponseType.Raw, 'JOIN {0}'.format(channel), ''))
            return responses
        else:
            return IRCResponse(ResponseType.Say,
                               "{0}, you didn't say where I should join".format(message.User.Name),
                               message.ReplyTo)

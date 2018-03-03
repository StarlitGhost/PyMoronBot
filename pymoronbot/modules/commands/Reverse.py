# -*- coding: utf-8 -*-
"""
Created on Nov 07, 2014

@author: Tyranic-Moron
"""
from twisted.plugin import IPlugin
from pymoronbot.moduleinterface import IModule
from pymoronbot.modules.commandinterface import BotCommand
from zope.interface import implementer

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType


@implementer(IPlugin, IModule)
class Reverse(BotCommand):
    def triggers(self):
        return ['reverse', 'backwards']

    def help(self, query):
        return 'reverse <text> - reverses the text given to it'

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) > 0:
            return IRCResponse(ResponseType.Say, message.Parameters[::-1], message.ReplyTo)
        else:
            return IRCResponse(ResponseType.Say, 'Reverse what?', message.ReplyTo)


reverse = Reverse()

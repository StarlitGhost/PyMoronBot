# -*- coding: utf-8 -*-
"""
Created on Dec 20, 2011

@author: Tyranic-Moron
"""
from twisted.plugin import IPlugin
from pymoronbot.moduleinterface import IModule
from pymoronbot.modules.commandinterface import BotCommand
from zope.interface import implementer

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType


@implementer(IPlugin, IModule)
class Say(BotCommand):
    def triggers(self):
        return ['say']

    def help(self, query):
        return 'say [channel] <text> - makes the bot repeat the specified text'

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if not message.ParameterList:
            return IRCResponse(ResponseType.Say, 'Say what?', message.ReplyTo)
        
        if message.ParameterList[0] in self.bot.channels:
            return IRCResponse(ResponseType.Say, u" ".join(message.ParameterList[1:]), message.ParameterList[0])
        
        return IRCResponse(ResponseType.Say, message.Parameters, message.ReplyTo)


say = Say()

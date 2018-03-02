# -*- coding: utf-8 -*-
"""
Created on Oct 16, 2014

@author: Tyranic-Moron
"""
from twisted.plugin import IPlugin
from pymoronbot.moduleinterface import IModule
from pymoronbot.modules.commandinterface import BotCommand
from zope.interface import implementer

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType


@implementer(IPlugin, IModule)
class Notice(BotCommand):
    def triggers(self):
        return ['notice']

    def help(self, query):
        return 'notice <target> <text> - makes the bot send the specified text as a notice to the specified target'

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) > 1:
            return IRCResponse(ResponseType.Notice, " ".join(message.ParameterList[1:]), message.ParameterList[0])
        else:
            return IRCResponse(ResponseType.Say, self.help(None), message.ReplyTo)


notice = Notice()

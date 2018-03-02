# -*- coding: utf-8 -*-
"""
Created on Dec 20, 2011

@author: Tyranic-Moron
"""
from twisted.plugin import IPlugin
from pymoronbot.moduleinterface import IModule
from pymoronbot.modules.commandinterface import BotCommand, admin
from zope.interface import implementer

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType


@implementer(IPlugin, IModule)
class Leave(BotCommand):
    def triggers(self):
        return ['leave', 'gtfo']

    def help(self, query):
        return "leave/gtfo - makes the bot leave the current channel"

    @admin('Only my admins can tell me to leave')
    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) > 0:
            return IRCResponse(ResponseType.Raw, 'PART {} :{}'.format(message.ReplyTo, message.Parameters), '')
        else:
            return IRCResponse(ResponseType.Raw, 'PART {} :toodles!'.format(message.ReplyTo), '')


leave = Leave()

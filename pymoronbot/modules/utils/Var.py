# -*- coding: utf-8 -*-
"""
Created on Mar 09, 2016
@author: Tyranic-Moron
"""
from twisted.plugin import IPlugin
from pymoronbot.moduleinterface import IModule
from pymoronbot.modules.commandinterface import BotCommand
from zope.interface import implementer

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType


@implementer(IPlugin, IModule)
class Var(BotCommand):
    def triggers(self):
        return ['var']

    def help(self, query):
        return "var <varname> <value> - sets <varname> to <value>, which can be accessed later using $<varname>. " \
           "the variables don't persist between messages, so it is only useful as a support function for aliases using sub and/or chain"

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        
        if len(message.ParameterList) < 1:
            return IRCResponse(ResponseType.Say, "You didn't give a variable name!", message.ReplyTo)
            
        varname = message.ParameterList[0]
        value = u' '.join(message.Parameters.split(' ')[1:])
        return IRCResponse(ResponseType.Say, "", message.ReplyTo, extraVars={varname: value})


var = Var()

# -*- coding: utf-8 -*-
"""
Created on May 26, 2014

@author: Tyranic-Moron
"""
from twisted.plugin import IPlugin
from pymoronbot.moduleinterface import IModule
from pymoronbot.modules.commandinterface import BotCommand
from zope.interface import implementer

import datetime

from twisted.internet import task
from twisted.internet import reactor
from pytimeparse.timeparse import timeparse

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType
from pymoronbot.utils import string


@implementer(IPlugin, IModule)
class Delay(BotCommand):
    def triggers(self):
        return ['delay', 'later']

    def help(self, query):
        return 'delay <duration> <command> (<parameters>) - executes the given command after the specified delay'

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) < 2:
            return IRCResponse(ResponseType.Say, self.help(None), message.ReplyTo)

        command = message.ParameterList[1].lower()
        delay = timeparse(message.ParameterList[0])
        delayDelta = datetime.timedelta(seconds=delay)
        delayString = string.deltaTimeToString(delayDelta, 's')
        params = message.ParameterList[2:]
        commandString = u'{}{} {}'.format(self.bot.commandChar, command, u' '.join(params))
        commandString = commandString.replace('$delayString', delayString)
        commandString = commandString.replace('$delay', str(delay))

        newMessage = IRCMessage(message.Type, message.User.String, message.Channel, commandString, self.bot)

        moduleHandler = self.bot.moduleHandler
        if command in moduleHandler.mappedTriggers:
            d = task.deferLater(reactor, delay, moduleHandler.mappedTriggers[command].execute, newMessage)
            d.addCallback(self.bot.sendResponse)
            return IRCResponse(ResponseType.Say,
                               "OK, I'll execute that in {}".format(delayString),
                               message.ReplyTo,
                               {'delay': delay, 'delayString': delayString})
        else:
            if 'Alias' not in moduleHandler.commands:
                return IRCResponse(ResponseType.Say,
                                   "'{}' is not a recognized command".format(command),
                                   message.ReplyTo)

            if command not in moduleHandler.commands['Alias'].aliases:
                return IRCResponse(ResponseType.Say,
                                   "'{}' is not a recognized command or alias".format(command),
                                   message.ReplyTo)

            d = task.deferLater(reactor, delay, moduleHandler.commands['Alias'].execute, newMessage)
            d.addCallback(self.bot.sendResponse)
            return IRCResponse(ResponseType.Say,
                               "OK, I'll execute that in {}".format(delayString),
                               message.ReplyTo)


delay = Delay()

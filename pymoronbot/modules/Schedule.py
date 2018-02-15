# -*- coding: utf-8 -*-
"""
Created on Feb 15, 2018

@author: Tyranic-Moron
"""

import datetime

from croniter import croniter
from twisted.internet import task
from twisted.internet import reactor
from pytimeparse.timeparse import timeparse

from pymoronbot.moduleinterface import ModuleInterface
from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType
from pymoronbot.utils import string


class Event(object):
    def __init__(self, cronStr, command, params):
        self.cronStr = cronStr
        self.command = command
        self.params = params

        cron = croniter(cronStr, datetime.datetime.utcnow())
        nextTime = cron.get_next(datetime.datetime)
        delta = nextTime - datetime.datetime.utcnow()
        seconds = delta.total_seconds()




class Schedule(ModuleInterface):
    triggers = ['schedule']
    help = 'schedule min hour day month day_of_week <title> <command> (<parameters>) - executes the given command at the times specified by the'

    schedule = {}

    def onLoad(self):
        # load schedule from data file, start them all going
        pass

    def onUnload(self):
        # cancel everything
        pass

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) < 7:
            return IRCResponse(ResponseType.Say, self.help, message.ReplyTo)

        cronStr = u' '.join(message.ParameterList[0:5])
        title = message.ParameterList[6]
        command = message.ParameterList[7].lower()
        params = message.ParameterList[8:]
        self.schedule[title] = Event(cronStr, command, params)

        #commandString = u'{}{} {}'.format(self.bot.commandChar, command, u' '.join(params))

        #newMessage = IRCMessage(message.Type, message.User.String, message.Channel, commandString, self.bot)

        #moduleHandler = self.bot.moduleHandler
        #if command in moduleHandler.mappedTriggers:
        #    d = task.deferLater(reactor, delay, moduleHandler.mappedTriggers[command].execute, newMessage)
        #    d.addCallback(self.bot.sendResponse)
        #    return IRCResponse(ResponseType.Say,
        #                       "OK, I'll execute that in {}".format(delayString),
        #                       message.ReplyTo,
        #                       {'delay': delay, 'delayString': delayString})

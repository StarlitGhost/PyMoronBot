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
from six import iteritems

from pymoronbot.moduleinterface import ModuleInterface
from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType
from pymoronbot.utils import string


class Task(object):
    def __init__(self, cronStr, command, params, user, channel, bot):
        self.cronStr = cronStr
        self.commandStr = command
        self.command = bot.moduleHandler.mappedTriggers[command].execute
        self.params = params
        self.user = user
        self.channel = channel
        self.bot = bot
        self.task = None

        self.cron = croniter(self.cronStr, datetime.datetime.utcnow())
        self.nextTime = self.cron.get_next(datetime.datetime)

    def start(self):
        delta = self.nextTime - datetime.datetime.utcnow()
        seconds = delta.total_seconds()
        self.task = task.deferLater(reactor, seconds, self.activate)
        self.task.addCallback(self.cycle)

    def activate(self):
        commandStr = u'{}{} {}'.format(self.bot.commandChar, self.commandStr,
                                       u' '.join(self.params))
        message = IRCMessage('PRIVMSG', self.user, self.channel,
                             commandStr,
                             self.bot)

        return self.command(message)

    def cycle(self, response):
        self.bot.sendResponse(response)
        self.nextTime = self.cron.get_next(datetime.datetime)
        self.start()

    def stop(self):
        if self.task:
            self.task.cancel()


class Schedule(ModuleInterface):
    triggers = ['schedule']
    help = 'schedule min hour day month day_of_week <title> <command> (<parameters>) - executes the given command at the times specified by the'

    schedule = {}

    def onLoad(self):
        # load schedule from data file, start them all going
        pass

    def onUnload(self):
        # cancel everything
        for _, t in iteritems(self.schedule):
            t.stop()

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) < 7:
            return IRCResponse(ResponseType.Say, self.help, message.ReplyTo)

        cronStr = u' '.join(message.ParameterList[0:5])
        title = message.ParameterList[5]
        command = message.ParameterList[6].lower()
        params = message.ParameterList[7:]
        self.schedule[title] = Task(cronStr, command, params,
                                    message.User.String, message.Channel,
                                    self.bot)
        self.schedule[title].start()

        #moduleHandler = self.bot.moduleHandler
        #if command in moduleHandler.mappedTriggers:
        #    d = task.deferLater(reactor, delay, moduleHandler.mappedTriggers[command].execute, newMessage)
        #    d.addCallback(self.bot.sendResponse)
        #    return IRCResponse(ResponseType.Say,
        #                       "OK, I'll execute that in {}".format(delayString),
        #                       message.ReplyTo,
        #                       {'delay': delay, 'delayString': delayString})

# -*- coding: utf-8 -*-
"""
Created on Feb 28, 2018

@author: Tyranic-Moron
"""

from twisted.plugin import IPlugin
from pymoronbot.moduleinterface import IModule, BotModule
from zope.interface import implementer


@implementer(IPlugin, IModule)
class CommandHandler(BotModule):
    def actions(self):
        return super(CommandHandler, self).actions() + [('message-channel', 1, self.handleCommand),
                                                        ('message-user', 1, self.handleCommand)]

    def handleCommand(self, message):
        if message.Command:
            return self.bot.moduleHandler.runGatheringAction('botmessage', message)


commandhandler = CommandHandler()

# -*- coding: utf-8 -*-
"""
Created on May 11, 2014

@author: Tyranic-Moron
"""

from twisted.plugin import IPlugin
from pymoronbot.moduleinterface import IModule, BotModule
from zope.interface import implementer

from pymoronbot.utils import string


@implementer(IPlugin, IModule)
class StripColour(BotModule):
    def actions(self):
        return super(StripColour, self).actions() + [('response-message', 99, self.execute),
                                                     ('response-action', 99, self.execute),
                                                     ('response-notice', 99, self.execute)]

    def help(self, query):
        return "Automatic module that strips colours from responses " \
               "if colours are blocked by channel mode"

    def execute(self, response):
        """
        @type response: IRCResponse
        """
        channel = self.bot.getChannel(response.Target)
        if channel is not None and 'c' in channel.Modes:
            # strip formatting if colours are blocked on the channel
            response.Response = string.stripFormatting(response.Response)


stripcolour = StripColour()

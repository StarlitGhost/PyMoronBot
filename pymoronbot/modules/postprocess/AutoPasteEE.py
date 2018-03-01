# -*- coding: utf-8 -*-
"""
Created on May 21, 2014

@author: Tyranic-Moron
"""

from twisted.plugin import IPlugin
from pymoronbot.moduleinterface import IModule, BotModule
from zope.interface import implementer

from pymoronbot.utils import string, web


@implementer(IPlugin, IModule)
class AutoPasteEE(BotModule):
    def actions(self):
        return super(AutoPasteEE, self).actions() + [('response-message', 100, self.execute),
                                                     ('response-action', 100, self.execute),
                                                     ('response-notice', 100, self.execute)]

    def execute(self, response):
        """
        @type response: IRCResponse
        """
        limit = 700  # chars
        expire = 10  # minutes
        if len(response.Response) > limit:
            replaced = web.pasteEE(string.stripFormatting(response.Response),
                                   u'Response longer than {} chars intended for {}'.format(limit, response.Target),
                                   expire)

            response.Response = u'Response too long, pasted here instead: {} (Expires in {} minutes)'.format(replaced,
                                                                                                             expire)


autopasteee = AutoPasteEE()

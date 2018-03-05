# -*- coding: utf-8 -*-
"""
Created on May 20, 2014

@author: Tyranic-Moron
"""
from twisted.plugin import IPlugin
from pymoronbot.moduleinterface import IModule
from pymoronbot.modules.commandinterface import BotCommand
from zope.interface import implementer

import re

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType

from pymoronbot.utils import string


@implementer(IPlugin, IModule)
class Find(BotCommand):
    def triggers(self):
        return ['find', 'google', 'g']

    def help(self, query):
        return 'find/google/g <searchterm> - returns the first google result for the given search term'

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        try:
            results = self.bot.moduleHandler.runActionUntilValue('search-web', message.Parameters)

            if not results:
                return IRCResponse(ResponseType.Say,
                                   u'[google developer key missing]',
                                   message.ReplyTo)

            firstResult = results[u'items'][0]

            title = firstResult[u'title']
            title = re.sub(r'\s+', ' ', title)
            content = firstResult[u'snippet']
            content = re.sub(r'\s+', ' ', content)  # replace multiple spaces with single ones (includes newlines?)
            content = string.unescapeXHTML(content)
            url = firstResult[u'link']
            replyText = u'{1}{0}{2}{0}{3}'.format(string.graySplitter, title, content, url)

            return IRCResponse(ResponseType.Say, replyText, message.ReplyTo)
        except Exception as x:
            print(str(x))
            return IRCResponse(ResponseType.Say, x.args, message.ReplyTo)


find = Find()

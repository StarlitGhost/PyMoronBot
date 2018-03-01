# -*- coding: utf-8 -*-
"""
Created on May 20, 2014

@author: Tyranic-Moron
"""
import re

from pymoronbot.modules.commandinterface import BotCommand
from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType

from pymoronbot.utils import string, web


class Find(BotCommand):
    triggers = ['find', 'google', 'g']
    help = 'find/google/g <searchterm> - returns the first google result for the given search term'
    runInThread = True

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        try:
            results = web.googleSearch(message.Parameters)

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

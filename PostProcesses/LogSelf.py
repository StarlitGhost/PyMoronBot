# -*- coding: utf-8 -*-
"""
Created on May 11, 2014

@author: Tyranic-Moron
"""

from PostProcessInterface import PostProcessInterface
from IRCResponse import IRCResponse, ResponseType
from Commands.Log import log


logFuncs = {ResponseType.Say: lambda nick, r: u'<{0}> {1}'.format(nick, r.Response),
            ResponseType.Do: lambda nick, r: u'*{0} {1}*'.format(nick, r.Response),
            ResponseType.Notice: lambda nick, r: u'[{0}] {1}'.format(nick, r.Response)}


class LogSelf(PostProcessInterface):

    priority = -1

    def execute(self, response):
        """
        @type response: IRCResponse
        """
        if response.Type in logFuncs:
            logString = logFuncs[response.Type](self.bot.nickname, response)
            log(logString, response.Target)

        return response
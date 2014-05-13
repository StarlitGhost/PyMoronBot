# -*- coding: utf-8 -*-
"""
Created on May 11, 2014

@author: Tyranic-Moron
"""

from moronbot import MoronBot
from PostProcessInterface import PostProcessInterface
from IRCResponse import IRCResponse, ResponseType
from GlobalVars import CurrentNick
from Commands.Log import log


logFuncs = {ResponseType.Say: lambda r: u'<{0}> {1}'.format(CurrentNick, r.Response),
            ResponseType.Do: lambda r: u'*{0} {1}*'.format(CurrentNick, r.Response),
            ResponseType.Notice: lambda r: u'[{0}] {1}'.format(CurrentNick, r.Response)}


class LogSelf(PostProcessInterface):

    priority = -1

    def execute(self, response, bot):
        """
        @type response: IRCResponse
        @type bot: MoronBot
        """
        if response.Type in logFuncs:
            logString = logFuncs[response.Type](response)
            log(logString, response.Target)

        return response
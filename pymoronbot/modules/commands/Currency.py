# -*- coding: utf-8 -*-
"""
Created on Dec 06, 2016

@author: Tyranic-Moron
"""
from twisted.plugin import IPlugin
from pymoronbot.moduleinterface import IModule
from pymoronbot.modules.commandinterface import BotCommand
from zope.interface import implementer

import json
from six import iteritems

from twisted.words.protocols.irc import assembleFormattedText, attributes as A

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType


@implementer(IPlugin, IModule)
class Currency(BotCommand):
    def triggers(self):
        return ['currency']

    def help(self, query):
        return "currency [<amount>] <from> in <to> - converts <amount> in <from> currency to <to> currency"

    runInThread = True

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) < 3:
            return IRCResponse(ResponseType.Say, self.help(None), message.ReplyTo)

        try:
            amount = float(message.ParameterList[0])
            offset = 1
        except ValueError:
            amount = 1.0
            offset = 0

        ccFrom = message.ParameterList[offset].upper()
        ccTo   = message.ParameterList[offset+2:]
        ccTo   = ",".join(ccTo)
        ccTo   = ccTo.upper()

        url = "https://api.fixer.io/latest?base={}&symbols={}"
        url = url.format(ccFrom, ccTo)
        response = self.bot.moduleHandler.runActionUntilValue('fetch-url', url)
        jsonResponse = json.loads(response.body)
        rates = jsonResponse['rates']

        if not rates:
            return IRCResponse(ResponseType.Say,
                               "Some or all of those currencies weren't recognized!",
                               message.ReplyTo)

        data = []
        for curr,rate in iteritems(rates):
            data.append("{} {}".format(rate*amount, curr))

        graySplitter = assembleFormattedText(A.normal[' ', A.fg.gray['|'], ' '])
        return IRCResponse(ResponseType.Say, graySplitter.join(data), message.ReplyTo)


currency = Currency()

# -*- coding: utf-8 -*-
"""
Created on Dec 06, 2016

@author: Tyranic-Moron
"""
import json

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface

from Utils import WebUtils

from twisted.words.protocols.irc import assembleFormattedText, attributes as A


class Currency(CommandInterface):
    triggers = ['currency']
    help = "currency [<amount>] <from> in <to> - converts <amount> in <from> currency to <to> currency"
    runInThread = True

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) < 3:
            return IRCResponse(ResponseType.Say, self.help, message.ReplyTo)

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
        response = WebUtils.fetchURL(url)
        jsonResponse = json.loads(response.body)
        rates = jsonResponse['rates']

        if not rates:
            return IRCResponse(ResponseType.Say,
                               "Some or all of those currencies weren't recognized!",
                               message.ReplyTo)

        data = []
        for curr,rate in rates.iteritems():
            data.append("{} {}".format(rate*amount, curr))

        graySplitter = assembleFormattedText(A.normal[' ', A.fg.gray['|'], ' '])
        return IRCResponse(ResponseType.Say, graySplitter.join(data), message.ReplyTo)

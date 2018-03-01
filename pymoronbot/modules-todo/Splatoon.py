# -*- coding: utf-8 -*-
"""
Created on Sep 01, 2017

@author: Tyranic-Moron
"""
import json
import time
import datetime

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType
from pymoronbot.modules.commandinterface import BotCommand

from pymoronbot.utils import string, web

from twisted.words.protocols.irc import assembleFormattedText, attributes as A


class Splatoon(BotCommand):
    triggers = ['splat']
    help = "splat [regular/ranked/league/fest]"
    runInThread = True

    graySplitter = assembleFormattedText(A.normal[' ', A.fg.gray['|'], ' '])

    def _fetch(self, j, short, mode, label):
        r = j[mode]
        data = []
        t = A.normal[A.bold['{} {}: '.format(label, r[0]['rule']['name'])],
                     '/'.join([r[0]['stage_a']['name'], r[0]['stage_b']['name']])]
        data.append(assembleFormattedText(t))
        if not short:
            # include next maps
            now = int(time.time())
            startTime = r[1]['startTime']
            delta = startTime - now
            d = datetime.timedelta(seconds=delta)
            deltaStr = string.deltaTimeToString(d, resolution='m')
            t = A.normal[A.bold['{} {} in {}: '.format(label, r[1]['rule']['name'], deltaStr)],
                         '/'.join([r[1]['stage_a']['name'], r[1]['stage_b']['name']])]
            data.append(assembleFormattedText(t))
        return ' | '.join(data)

    def _regular(self, j, short):
        return self._fetch(j, short, 'regular', 'Regular')

    def _ranked(self, j, short):
        return self._fetch(j, short, 'gachi', 'Ranked')

    def _league(self, j, short):
        return self._fetch(j, short, 'league', 'League')

    def _fest(self, j, short):
        if j['splatfests']:
            pass
        elif not short:
            return 'No SplatFest is currently scheduled'

    def execute(self, message):
        """
        @type message: IRCMessage
        """

        url = "https://splatoon2.ink/data/schedules.json"
        response = web.fetchURL(url)
        jsonResponse = json.loads(response.body)

        if len(message.ParameterList) < 1:
            # do everything
            data = []
            data += filter(None, [self._regular(jsonResponse, short=True)])
            data += filter(None, [self._ranked(jsonResponse, short=True)])
            data += filter(None, [self._league(jsonResponse, short=True)])
            data += filter(None, [self._fest(jsonResponse, short=True)])
            return IRCResponse(ResponseType.Say,
                               self.graySplitter.join(data),
                               message.ReplyTo)
        else:
            subCommands = {
                'regular': self._regular,
                'ranked': self._ranked,
                'league': self._league,
                'fest': self._fest
            }
            subCommand = message.ParameterList[0].lower()
            if subCommand in subCommands:
                return IRCResponse(ResponseType.Say,
                                   subCommands[subCommand](jsonResponse, short=False),
                                   message.ReplyTo)
            else:
                return IRCResponse(ResponseType.Say, self.help, message.ReplyTo)

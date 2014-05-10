"""
Created on Dec 13, 2011

@author: Tyranic-Moron
"""

import re
import datetime

from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType


class Data(object):
    lastCode = None
    lastDate = None
    lastUser = None


class Command(CommandInterface):
    triggers = ['hangout', 'hangoot']
    help = 'hangout - gives you the last posted G+ hangout link'

    hangoutDict = {}

    def shouldExecute(self, message=IRCMessage):
        if message.Type in self.acceptedTypes:
            return True

    def execute(self, message=IRCMessage):
        match = re.search('^hango+?u?t$', message.Command, re.IGNORECASE)
        if match:
            if message.ReplyTo not in self.hangoutDict:
                self.hangoutDict[message.ReplyTo] = None
            if self.hangoutDict[message.ReplyTo] is None:
                return IRCResponse(ResponseType.Say,
                                   'No hangouts posted here yet',
                                   message.ReplyTo)

            hangout = self.hangoutDict[message.ReplyTo]

            timeDiff = datetime.datetime.utcnow() - hangout.lastDate
            url = 'https://talkgadget.google.com/hangouts/_/{0}'.format(hangout.lastCode)
            byLine = 'first posted {0} ago by {1}'.format(
                self.strfdelta(timeDiff, '{days} day(s) {hours} hour(s) {minutes} minute(s)'), hangout.lastUser)

            response = 'Last hangout posted: {0} ({1})'.format(url, byLine)

            return IRCResponse(ResponseType.Say, response, message.ReplyTo)

        match = re.search(r'google\.com/hangouts/_/(?P<code>[^\?\s]+)',
                          message.MessageString,
                          re.IGNORECASE)

        if not match:
            return

        if message.ReplyTo not in self.hangoutDict or self.hangoutDict[message.ReplyTo] is None:
            self.hangoutDict[message.ReplyTo] = Data()
        elif match.group('code') == self.hangoutDict[message.ReplyTo].lastCode:
            return

        self.hangoutDict[message.ReplyTo].lastCode = match.group('code')
        self.hangoutDict[message.ReplyTo].lastUser = message.User.Name
        self.hangoutDict[message.ReplyTo].lastDate = datetime.datetime.utcnow()
        return

    @staticmethod
    def strfdelta(tdelta, fmt):
        d = {"days": tdelta.days}
        d["hours"], rem = divmod(tdelta.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)
        return fmt.format(**d)

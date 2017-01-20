# -*- coding: utf-8 -*-
"""
Created on Jan 20, 2017

@author: Tyranic-Moron
"""

from collections import OrderedDict

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface

import parsedatetime


class Time(CommandInterface):
    triggers = ['time', 'date']
    
    def onLoad(self):
        self.cal = parsedatetime.Calendar()

    def _time(self, query):
        """time <natural language time query> - returns time from natural language queries (eg: in 100 minutes (at 18:00) => 19:40:00)"""
        (date, _) = self.cal.parseDT(query)
        return "{:%H:%M:%S%z}".format(date)

    def _date(self, query):
        """date <natural language date query> - returns dates from natural language queries (eg: friday next week => 2017-02-03)"""
        (date, _) = self.cal.parseDT(query)
        return "{:%Y-%m-%d}".format(date)

    _commands = OrderedDict([
        (u'time', _time),
        (u'date', _date),
        ])

    def help(self, message):
        """
        @type message: IRCMessage
        """
        return self._commands[message.Command].__doc__

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        response = self._commands[message.Command](self, message.Parameters)
        return IRCResponse(ResponseType.Say, response, message.ReplyTo)


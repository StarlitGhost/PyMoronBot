# -*- coding: utf-8 -*-
"""
Created on Dec 05, 2013

@author: Tyranic-Moron
"""
import random

from pymoronbot.modules.commandinterface import BotCommand
from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType

from pymoronbot.utils import web


class Gif(BotCommand):
    triggers = ['gif']
    help = 'gif [<year>] - fetches a random gif posted during Desert Bus'
    
    def execute(self, message):
        """
        @type message: IRCMessage
        """

        baseURL = "http://greywool.com/desertbus/{}/gifs/random.php"
        years = range(7, 11)

        if len(message.ParameterList) > 0:
            invalid = u"'{}' is not a valid year, valid years are {} to {}"\
                .format(message.ParameterList[0], years[0], years[-1])
            try:
                if len(message.ParameterList[0]) < 4:
                    year = int(message.ParameterList[0])
                else:
                    raise ValueError
            except ValueError:
                return IRCResponse(ResponseType.Say, invalid, message.ReplyTo)

            if year not in years:
                return IRCResponse(ResponseType.Say, invalid, message.ReplyTo)
        else:
            year = random.choice(years)

        url = baseURL.format(year)

        webPage = web.fetchURL(url)

        link = webPage.body

        return IRCResponse(ResponseType.Say,
                           u"Random DB{} gif: {}".format(year, link),
                           message.ReplyTo)

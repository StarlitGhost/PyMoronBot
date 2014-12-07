# -*- coding: utf-8 -*-
"""
Created on Dec 05, 2013

@author: Tyranic-Moron
"""
import random

from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType

from Utils import WebUtils


class Gif(CommandInterface):
    triggers = ['gif']
    help = 'gif [<year>] - fetches a random gif posted during Desert Bus'
    
    def execute(self, message):
        """
        @type message: IRCMessage
        """

        baseURL = "http://greywool.com/desertbus/{}/gifs/random.php"
        years = range(7, 9)

        if len(message.ParameterList) > 0:
            invalid = u"'{}' is not a valid year, valid years are {} to {}"\
                .format(message.ParameterList[0], years[0], years[-1])
            try:
                year = int(message.ParameterList[0])
            except ValueError:
                return IRCResponse(ResponseType.Say, invalid, message.ReplyTo)

            if year not in years:
                return IRCResponse(ResponseType.Say, invalid, message.ReplyTo)
        else:
            year = random.choice(years)

        url = baseURL.format(year)

        webPage = WebUtils.fetchURL(url)

        link = webPage.body

        return IRCResponse(ResponseType.Say,
                           u"Random DB{} gif: {}".format(year, link),
                           message.ReplyTo)

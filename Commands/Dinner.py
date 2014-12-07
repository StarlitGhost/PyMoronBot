# -*- coding: utf-8 -*-
"""
Created on Jul 31, 2013

@author: Tyranic-Moron, Emily
"""

from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType

from Utils import WebUtils

from bs4 import BeautifulSoup


class Dinner(CommandInterface):
    triggers = ['dinner']
    help = 'dinner (meat/veg/drink) - asks WhatTheFuckShouldIMakeForDinner.com' \
           ' what you should make for dinner'
    
    def execute(self, message):
        """
        @type message: IRCMessage
        """
        wtfsimfd = "http://whatthefuckshouldimakefordinner.com/{}"

        options = {'meat': 'index.php', 'veg': 'veg.php', 'drink': 'drinks.php'}

        option = 'meat'
        if len(message.ParameterList) > 0:
            option = message.ParameterList[0]

        if option in options:
            webPage = WebUtils.fetchURL(wtfsimfd.format(options[option]))

            soup = BeautifulSoup(webPage.body)

            phrase = soup.find('dl').text
            item = soup.find('a')
            link = WebUtils.shortenGoogl(item['href'])

            return IRCResponse(ResponseType.Say,
                               u"{}... {} {}".format(phrase, item.text, link),
                               message.ReplyTo)

        else:
            error = u"'{}' is not a recognized dinner type, please choose one of {}"\
                .format(option, u'/'.join(options.keys()))
            return IRCResponse(ResponseType.Say, error, message.ReplyTo)

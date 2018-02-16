# -*- coding: utf-8 -*-
"""
Created on Jul 31, 2013

@author: Tyranic-Moron, Emily
"""

from bs4 import BeautifulSoup

from pymoronbot.moduleinterface import ModuleInterface
from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType

from pymoronbot.utils import web


class Dinner(ModuleInterface):
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
            webPage = web.fetchURL(wtfsimfd.format(options[option]))

            soup = BeautifulSoup(webPage.body, 'lxml')

            phrase = soup.find('dl').text
            item = soup.find('a')
            link = web.shortenGoogl(item['href'])

            return IRCResponse(ResponseType.Say,
                               u"{}... {} {}".format(phrase, item.text, link),
                               message.ReplyTo)

        else:
            error = u"'{}' is not a recognized dinner type, please choose one of {}"\
                .format(option, u'/'.join(options.keys()))
            return IRCResponse(ResponseType.Say, error, message.ReplyTo)

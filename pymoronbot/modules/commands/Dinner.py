# -*- coding: utf-8 -*-
"""
Created on Jul 31, 2013

@author: Tyranic-Moron, Emily
"""
from twisted.plugin import IPlugin
from pymoronbot.moduleinterface import IModule
from pymoronbot.modules.commandinterface import BotCommand
from zope.interface import implementer

from bs4 import BeautifulSoup

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType


@implementer(IPlugin, IModule)
class Dinner(BotCommand):
    def triggers(self):
        return ['dinner']

    def help(self, query):
        return 'dinner (meat/veg/drink) - asks WhatTheFuckShouldIMakeForDinner.com' \
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
            webPage = self.bot.moduleHandler.runActionUntilValue('fetch-url', wtfsimfd.format(options[option]))

            soup = BeautifulSoup(webPage.body, 'lxml')

            phrase = soup.find('dl').text
            item = soup.find('a')
            link = self.bot.moduleHandler.runActionUntilValue('shorten-url', item['href'])

            return IRCResponse(ResponseType.Say,
                               u"{}... {} {}".format(phrase, item.text, link),
                               message.ReplyTo)

        else:
            error = u"'{}' is not a recognized dinner type, please choose one of {}"\
                .format(option, u'/'.join(options.keys()))
            return IRCResponse(ResponseType.Say, error, message.ReplyTo)


dinner = Dinner()

'''
Created on Jul 31, 2013

@author: Tyranic-Moron, Emily
'''

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
import GlobalVars

import re

import WebUtils

from bs4 import BeautifulSoup

class Command(CommandInterface):
    triggers = ['dinner']
    help = 'dinner (meat/veg/drink) - asks WhatTheFuckShouldIMakeForDinner.com what you should make for dinner'
    
    def execute(self, message):
        wtfsimfd = "http://whatthefuckshouldimakefordinner.com/{0}"

        options = {'meat': 'index.php', 'veg': 'veg.php', 'drink': 'drinks.php'}

        option = 'meat'
        if len(message.ParameterList) > 0:
            option = message.ParameterList[0]

        if option in options:
            webPage = WebUtils.FetchURL(wtfsimfd.format(options[option]))

            soup = BeautifulSoup(webPage.Page)

            phrase = soup.find('dl').text
            item = soup.find('a')
            link = WebUtils.ShortenGoogl(item['href'])

            return IRCResponse(ResponseType.Say, u"{0}... {1} {2}".format(phrase, item.text, link), message.ReplyTo)

        else:
            return IRCResponse(ResponseType.Say, u"'{0}' is not a recognized dinner type, please choose one of {1}".format(option, u'/'.join(options.keys())), message.ReplyTo)

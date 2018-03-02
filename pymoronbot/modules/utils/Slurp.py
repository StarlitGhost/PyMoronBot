# -*- coding: utf-8 -*-
"""
Created on Aug 31, 2015

@author: Tyranic-Moron
"""
from twisted.plugin import IPlugin
from pymoronbot.moduleinterface import IModule
from pymoronbot.modules.commandinterface import BotCommand
from zope.interface import implementer

from html.parser import HTMLParser
import re
from six import string_types

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType

from pymoronbot.utils import web

from bs4 import BeautifulSoup


@implementer(IPlugin, IModule)
class Slurp(BotCommand):
    def triggers(self):
        return ['slurp']

    def help(self, query):
        return "slurp <attribute> <url> <css selector> - scrapes the given attribute from the tag selected " \
            "at the given url"

    htmlParser = HTMLParser()

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) < 3:
            return IRCResponse(ResponseType.Say, u"Not enough parameters, usage: {}".format(self.help), message.ReplyTo)

        prop, url, selector = (message.ParameterList[0], message.ParameterList[1], u" ".join(message.ParameterList[2:]))

        if not re.match(r'^\w+://', url):
            url = u"http://{}".format(url)

        if 'slurp' in message.Metadata and url in message.Metadata['slurp']:
            soup = message.Metadata['slurp'][url]
        else:
            page = web.fetchURL(url)
            if page is None:
                return IRCResponse(ResponseType.Say, u"Problem fetching {}".format(url), message.ReplyTo)
            soup = BeautifulSoup(page.body, 'lxml')

        tag = soup.select_one(selector)

        if tag is None:
            return IRCResponse(ResponseType.Say,
                               u"'{}' does not select a tag at {}".format(selector, url),
                               message.ReplyTo)

        specials = {
            'tagname': tag.name,
            'text': tag.text
        }

        if prop in specials:
            value = specials[prop]
        elif prop in tag.attrs:
            value = tag[prop]
        else:
            return IRCResponse(ResponseType.Say,
                               u"The tag selected by '{}' ({}) does not have attribute '{}'".format(selector,
                                                                                                    tag.name,
                                                                                                    prop),
                               message.ReplyTo)

        if not isinstance(value, string_types):
            value = u" ".join(value)

        # sanitize the value
        value = value.strip()
        value = re.sub(r'[\r\n]+', u' ', value)
        value = re.sub(r'\s+', u' ', value)
        value = self.htmlParser.unescape(value)

        return IRCResponse(ResponseType.Say, value, message.ReplyTo,
                           extraVars={'slurpURL': url},
                           metadata={'slurp': {url: soup}})


slurp = Slurp()

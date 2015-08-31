# -*- coding: utf-8 -*-
"""
Created on Aug 31, 2015

@author: Tyranic-Moron
"""

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface

from Utils import WebUtils

from bs4 import BeautifulSoup


class Slurp(CommandInterface):
    triggers = ['slurp']
    help = "slurp <attribute> <url> <css selector> - scrapes the given attribute from the tag selected at the given url"

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) < 3:
            return IRCResponse(ResponseType.Say, u"Not enough parameters, usage: {}".format(self.help), message.ReplyTo)

        prop, url, selector = (message.ParameterList[0], message.ParameterList[1], u" ".join(message.ParameterList[2:]))

        page = WebUtils.fetchURL(url)
        if page is None:
            return IRCResponse(ResponseType.Say, u"Problem fetching {}".format(url), message.ReplyTo)

        soup = BeautifulSoup(page.body)
        tag = soup.select_one(selector)

        if tag is None:
            return IRCResponse(ResponseType.Say,
                               u"'{}' does not select a tag at {}".format(selector, url),
                               message.ReplyTo)

        specials = {
            'name': tag.name,
            'text': tag.text
        }

        if prop in specials:
            value = specials[prop]
        elif prop in tag:
            value = tag[prop]
        else:
            return IRCResponse(ResponseType.Say,
                               u"The tag selected by '{}' ({}) does not have attribute '{}'".format(selector,
                                                                                                    tag.name,
                                                                                                    prop),
                               message.ReplyTo)

        if not isinstance(value, basestring):
            value = u" ".join(value)

        return IRCResponse(ResponseType.Say, value, message.ReplyTo)


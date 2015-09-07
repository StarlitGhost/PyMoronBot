# -*- coding: utf-8 -*-
"""
Created on Sep 07, 2015

@author: Tyranic-Moron
"""
import HTMLParser
import re

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface

from Utils import WebUtils

from jq import jq


class JQ(CommandInterface):
    triggers = ['jq']
    help = "jq <url> <filter> - filters json returned by the given url, returning values. \
filter syntax here: https://stedolan.github.io/jq/manual/#Basicfilters"

    htmlParser = HTMLParser.HTMLParser()

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) < 2:
            return IRCResponse(ResponseType.Say, u"Not enough parameters, usage: {}".format(self.help), message.ReplyTo)

        url, jqfilter = (message.ParameterList[0], u" ".join(message.ParameterList[1:]))

        if not re.match(ur'^\w+://', url):
            url = u"http://{}".format(url)

        page = WebUtils.fetchURL(url)
        if page is None:
            return IRCResponse(ResponseType.Say, u"Problem fetching {}".format(url), message.ReplyTo)

        try:
            value = jq(jqfilter).transform(text=page.body)
        except ValueError as e:
            response = re.sub(ur'[\r\n]+', u' ', e.message)
            return IRCResponse(ResponseType.Say, response, message.ReplyTo)

        if value is None:
            return IRCResponse(ResponseType.Say,
                               u"{} does not match a value".format(jqfilter),
                               message.ReplyTo)
        if isinstance(value, dict):
            return IRCResponse(ResponseType.Say,
                               u"{} matches a dict".format(jqfilter),
                               message.ReplyTo)
        if isinstance(value, list):
            return IRCResponse(ResponseType.Say,
                               u"{} matches a list".format(jqfilter),
                               message.ReplyTo)

        # sanitize the value
        value = u'{}'.format(value)
        value = value.strip()
        value = re.sub(ur'[\r\n]+', u' ', value)
        value = re.sub(ur'\s+', u' ', value)
        value = self.htmlParser.unescape(value)

        return IRCResponse(ResponseType.Say, value, message.ReplyTo)


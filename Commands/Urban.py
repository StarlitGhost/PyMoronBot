# -*- coding: utf-8 -*-
"""
Created on Jan 24, 2014

@author: Tyranic-Moron
"""

import urllib
import json

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface

from Utils import WebUtils

from twisted.words.protocols.irc import assembleFormattedText, attributes as A


class Urban(CommandInterface):
    triggers = ['urban', 'ud']
    help = "urban <search term> - returns the definition of the given search term from UrbanDictionary.com"
    
    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say,
                               "You didn't give a word! Usage: {0}".format(self.help),
                               message.ReplyTo)
        
        search = urllib.quote(message.Parameters)

        url = 'http://api.urbandictionary.com/v0/define?term={0}'.format(search)
        
        webPage = WebUtils.fetchURL(url)

        response = json.loads(webPage.body)

        if len(response['list']) == 0:
            return IRCResponse(ResponseType.Say, "No entry found for '{0}'".format(search), message.ReplyTo)

        graySplitter = assembleFormattedText(A.normal[' ', A.fg.gray['|'], ' '])

        defn = response['list'][0]

        word = defn['word']
        
        definition = defn['definition']
        definition = graySplitter.join([s.strip() for s in definition.strip().split('\r\n')])

        example = defn['example']
        example = graySplitter.join([s.strip() for s in example.strip().split('\r\n')])

        author = defn['author']

        up = defn['thumbs_up']
        down = defn['thumbs_down']
        
        more = 'http://{}.urbanup.com/'.format(word)

        if word.lower() != message.Parameters.lower():
            word = "{0} (Contains '{0}')".format(word, message.Parameters)

        defFormatString = unicode(assembleFormattedText(A.normal[A.bold["{0}:"], " {1}"]))
        exampleFormatString = unicode(assembleFormattedText(A.normal[A.bold["Example(s):"], " {0}"]))
        byFormatString = unicode(assembleFormattedText(A.normal["{0}",
                                                                graySplitter,
                                                                A.fg.lightGreen["+{1}"],
                                                                A.fg.gray["/"],
                                                                A.fg.lightRed["-{2}"],
                                                                graySplitter,
                                                                "More defs: {3}"]))
        responses = [IRCResponse(ResponseType.Say,
                                 defFormatString.format(word, definition),
                                 message.ReplyTo),
                     IRCResponse(ResponseType.Say,
                                 exampleFormatString.format(example),
                                 message.ReplyTo),
                     IRCResponse(ResponseType.Say,
                                 byFormatString.format(author, up, down, more),
                                 message.ReplyTo)]
        
        return responses

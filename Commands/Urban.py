"""
Created on Jan 24, 2014

@author: Tyranic-Moron
"""

import urllib

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
from moronbot import MoronBot

from Utils import WebUtils

from bs4 import BeautifulSoup
from twisted.words.protocols.irc import assembleFormattedText, attributes as A


class Urban(CommandInterface):
    triggers = ['urban', 'ud']
    help = "urban <search term> - returns the definition of the given search term from UrbanDictionary.com"
    
    def execute(self, message=IRCMessage, bot=MoronBot):
        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say,
                               "You didn't give a word! Usage: {0}".format(self.help),
                               message.ReplyTo)
        
        search = urllib.quote(message.Parameters)

        url = 'http://www.urbandictionary.com/define.php?term={0}'.format(search)
        
        webPage = WebUtils.fetchURL(url)

        soup = BeautifulSoup(webPage.Page)
        # replace link tags with their contents
        [a.unwrap() for a in soup.find_all('a')]

        box = soup.find('div', {'class' : 'box'})

        if not box:
            return IRCResponse(ResponseType.Say, "No entry found for '{0}'".format(search), message.ReplyTo)

        graySplitter = assembleFormattedText(A.normal[' ', A.fg.gray['|'], ' '])

        word = box.find('div', {'class' : 'word'}).text.strip()

        # 2014-01-28 really, urban dictionary? 'definition' to 'meaning'? what an important change!
        definition = box.find('div', {'class' : 'meaning'})
        if definition.br is not None:
            definition.br.replace_with('\n')
        definition = graySplitter.join([s.strip() for s in definition.text.strip().split('\n')])

        example = box.find('div', {'class' : 'example'})
        if example.br is not None:
            example.br.replace_with('\n')
        example = graySplitter.join([s.strip() for s in example.text.strip().split('\n')])

        author = box.find('div', {'class' : 'contributor'}).text.strip().replace('\n', ' ')

        counts = box.find('div', {'class' : 'thumbs-counts'}).find_all('span', {'class' : 'count'})
        up = counts[0].text
        down = counts[1].text

        if word.lower() != message.Parameters.lower():
            word = "{0} (Contains '{0}')".format(word, message.Parameters)

        formatString = assembleFormattedText(
                           A.normal[A.bold["{0}:"], " {1}\n",
                                    A.bold["Example(s):"], " {2}\n",
                                    "{3}", graySplitter,
                                    A.fg.lightGreen["+{4}"], A.fg.gray["/"], A.fg.lightRed["-{5}"], graySplitter,
                                    "More defs: {6}"])

        response = formatString.format(word, definition, example, author, up, down, url)
        
        return IRCResponse(ResponseType.Say, response, message.ReplyTo)

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
import WebUtils

import re
import urllib, urllib2
from bs4 import BeautifulSoup
from twisted.words.protocols.irc import assembleFormattedText, attributes as A

class Instantiate(Function):
    Help = "urban <search term> - returns the definition of the given search term from UrbanDictionary.com"
    
    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('^(urban|ud)$', message.Command, re.IGNORECASE)
        if not match:
            return
        
        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say, "You didn't give a word! Usage: {0}".format(self.Help), message.ReplyTo)
        
        search = urllib.quote(message.Parameters)

        url = 'http://www.urbandictionary.com/define.php?term={0}'.format(search)
        
        webPage = WebUtils.FetchURL(url)

        soup = BeautifulSoup(webPage.Page)

        box = soup.find('div', {'class' : 'box'})

        if not box:
            return IRCResponse(ResponseType.Say, "No entry found for '{0}'".format(search), message.ReplyTo)

        graySplitter = assembleFormattedText(A.normal[' ', A.fg.gray['|'], ' '])

        word = box.find('div', {'class' : 'word'}).text.strip()
        definition = graySplitter.join(box.find('div', {'class' : 'definition'}).stripped_strings)
        example = graySplitter.join(box.find('div', {'class' : 'example'}).stripped_strings)
        author = box.find('div', {'class' : 'contributor'}).text.strip().replace('\n', ' ')
        counts = box.find('div', {'class' : 'thumbs-counts'}).find_all('span', {'class' : 'count'})
        up = counts[0].text
        down = counts[1].text

        if word.lower() != message.Parameters.lower():
            word = "Contains '{0}'".format(word)

        formatString = assembleFormattedText(
                           A.normal[A.bold["{0}:"], " {1}\n",
                                    A.bold["Example(s):"], " {2}\n",
                                    "{3}", graySplitter,
                                    A.fg.lightGreen["+{4}"], "/", A.fg.lightRed["-{5}"], graySplitter, "More defs: {6}"])

        response = formatString.format(word, definition, example, author, up, down, url)
        
        return IRCResponse(ResponseType.Say, response, message.ReplyTo)

'''
Created on Dec 05, 2013

@author: Tyranic-Moron
'''

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
import GlobalVars

import re

import WebUtils

from bs4 import BeautifulSoup

class Instantiate(Function):

    Help = 'gif - fetches a random gif posted during Desert Bus'
    
    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('^(gif)$', message.Command, re.IGNORECASE)
        if not match:
            return

        url = "http://greywool.com/desertbus/gifs/random.php"

        webPage = WebUtils.FetchURL(url)

        link = webPage.Page

        return IRCResponse(ResponseType.Say, u"Random DB gif: {0}".format(link), message.ReplyTo)

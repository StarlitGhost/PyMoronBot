# -*- coding: utf-8 -*-
from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Utils import WebUtils

from bs4 import BeautifulSoup


class Etymology(CommandInterface):
    triggers = ['etym', 'etymology']
    help = "etym(ology) <word> - returns the etymology of the given word from etymonline.com"
    
    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say,
                               "You didn't give a word! Usage: {0}".format(self.help),
                               message.ReplyTo)
        
        word = message.Parameters
        
        webPage = WebUtils.fetchURL('http://www.etymonline.com/index.php?allowed_in_frame=0&search={0}'.format(word))
        root = BeautifulSoup(webPage.body)
        etymTitle = root.find('dt')
        etymDef = root.find('dd')
        
        if not etymTitle or not etymDef:
            return IRCResponse(ResponseType.Say,
                               "No etymology found for '{0}'".format(word),
                               message.ReplyTo)

        response = "{0}: {1}".format(etymTitle.text.strip(), etymDef.text.strip())
        
        return IRCResponse(ResponseType.Say,
                           response,
                           message.ReplyTo)

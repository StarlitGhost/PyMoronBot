# -*- coding: utf-8 -*-
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
from Utils import WebUtils
from moronbot import MoronBot

from bs4 import BeautifulSoup


class Down(CommandInterface):
    triggers = ['down', 'down?']
    help = "down(?) <url> - asks DownForEveryoneOrJustMe.com if the given url is down for everyone or just you"
    
    def execute(self, message, bot):
        """
        @type message: IRCMessage
        @type bot: MoronBot
        """
        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say, "You didn't give a URL! Usage: {0}".format(self.help), message.ReplyTo)

        url = message.Parameters
        
        webPage = WebUtils.fetchURL('http://www.downforeveryoneorjustme.com/{0}'.format(url))
        root = BeautifulSoup(webPage.Page)
        downText = root.find('div').text.splitlines()[1].strip()
        
        return IRCResponse(ResponseType.Say, downText, message.ReplyTo)

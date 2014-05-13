# -*- coding: utf-8 -*-
from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from moronbot import MoronBot

from Utils import WebUtils


class Googl(CommandInterface):
    triggers = ['googl', 'shorten', 'goo.gl']
    help = "googl/shorten <url> - Gives you a shortened version of a url, via Goo.gl"
    
    def execute(self, message, bot):
        """
        @type message: IRCMessage
        @type bot: MoronBot
        """
        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say, "You didn't give a URL to shorten!", message.ReplyTo)
        
        url = WebUtils.shortenGoogl(message.Parameters)
        
        return IRCResponse(ResponseType.Say, url, message.ReplyTo)

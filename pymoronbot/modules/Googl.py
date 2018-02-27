# -*- coding: utf-8 -*-
from pymoronbot.modules.commandinterface import BotCommand
from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType

from pymoronbot.utils import web


class Googl(BotCommand):
    triggers = ['googl', 'shorten', 'goo.gl']
    help = "googl/shorten <url> - Gives you a shortened version of a url, via Goo.gl"
    
    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say, "You didn't give a URL to shorten!", message.ReplyTo)
        
        url = web.shortenGoogl(message.Parameters)
        
        return IRCResponse(ResponseType.Say, url, message.ReplyTo)

# -*- coding: utf-8 -*-
from twisted.plugin import IPlugin
from pymoronbot.moduleinterface import IModule
from pymoronbot.modules.commandinterface import BotCommand
from zope.interface import implementer

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType

from pymoronbot.utils import web


@implementer(IPlugin, IModule)
class Googl(BotCommand):
    def triggers(self):
        return ['googl', 'shorten', 'goo.gl']

    def help(self, query):
        return "googl/shorten <url> - Gives you a shortened version of a url, via Goo.gl"
    
    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say, "You didn't give a URL to shorten!", message.ReplyTo)
        
        url = web.shortenGoogl(message.Parameters)
        
        return IRCResponse(ResponseType.Say, url, message.ReplyTo)


googl = Googl()

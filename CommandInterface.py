# -*- coding: utf-8 -*-
from moronbot import MoronBot
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType


class CommandInterface(object):
    triggers = []
    acceptedTypes = ['PRIVMSG']
    help = '<no help defined (yet)>'
    runInThread = False

    priority = 0
    
    def __init__(self, bot):
        """
        @type bot: MoronBot
        """
        self.onLoad(bot)

    def onLoad(self, bot):
        """
        @type bot: MoronBot
        """
        pass

    def onUnload(self, bot):
        """
        @type bot: MoronBot
        """
        pass

    def shouldExecute(self, message, bot):
        """
        @type message: IRCMessage
        @type bot: MoronBot
        """
        if message.Type not in self.acceptedTypes:
            return False
        if message.Command.lower() not in self.triggers:
            return False
        
        return True

    def execute(self, message, bot):
        """
        @type message: IRCMessage
        @type bot: MoronBot
        """
        return IRCResponse(ResponseType.Say, '<command not yet implemented>', message.ReplyTo)

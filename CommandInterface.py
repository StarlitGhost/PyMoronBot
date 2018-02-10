# -*- coding: utf-8 -*-
from fnmatch import fnmatch

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
        self.bot = bot
        self.onLoad()

    def onLoad(self):
        pass

    def onUnload(self):
        pass

    def checkPermissions(self, message):
        """
        @type message: IRCMessage
        @rtype Boolean
        """
        for owner in self.bot.config.getWithDefault('owners', []):
            if fnmatch(message.User.String, owner):
                return True
        for admin in self.bot.config.getWithDefault('admins', []):
            if fnmatch(message.User.String, admin):
                return True
        return False
    
    def shouldExecute(self, message):
        """
        @type message: IRCMessage
        @rtype Boolean
        """
        if message.Type not in self.acceptedTypes:
            return False
        if message.Command.lower() not in self.triggers:
            return False
        
        return True

    def execute(self, message):
        """
        @type message: IRCMessage
        @rtype IRCResponse | list[IRCResponse]
        """
        return IRCResponse(ResponseType.Say, '<command not yet implemented>', message.ReplyTo)

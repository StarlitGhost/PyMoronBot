# -*- coding: utf-8 -*-
from fnmatch import fnmatch
from functools import wraps, partial

from pymoronbot.moronbot import MoronBot
from pymoronbot.response import IRCResponse, ResponseType


def admin(func=None, msg=''):
    if callable(func):
        @wraps(func)
        def wrapped_func(inst, message):
            print(func)
            print(msg)

            if not inst.checkPermissions(message):
                if msg:
                    return IRCResponse(ResponseType.Say, msg, message.ReplyTo)
                else:
                    return IRCResponse(ResponseType.Say,
                                       "Only my admins may use {!r}".format(message.Command),
                                       message.ReplyTo)
            return func(inst, message)
        return wrapped_func
    else:
        return partial(admin, msg=func) # this seems wrong, should be msg=msg


def ignore(command):
    @wraps(command)
    def wrapped(inst, message):
        if not inst.checkIgnoreList(message):
            return
        return command(inst, message)
    return wrapped


class ModuleInterface(object):
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

    def checkIgnoreList(self, message):
        """
        @type message: IRCMessage
        @rtype Boolean
        """
        for ignore in self.bot.config.getWithDefault('ignored', []):
            if fnmatch(message.User.String, ignore):
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

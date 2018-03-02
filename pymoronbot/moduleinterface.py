# -*- coding: utf-8 -*-

from zope.interface import Interface
from functools import wraps
from fnmatch import fnmatch


class IModule(Interface):
    def actions():
        """
        Returns the list of actions this module hooks into.
        Actions are defined as a tuple with the following values:
        (action_name, priority, function)
        action_name (string): The name of the action.
        priority (int):       Actions are handled in order of priority.
                              Leave it at 1 unless you want to override another handler.
        function (reference): A reference to the function in the module that handles this action.
        """

    def onLoad():
        """
        Called when the module is loaded. Typically loading data, API keys, etc.
        """

    def hookBot(bot):
        """
        Called when the bot is loaded to pass a reference to the bot for later use.
        """

    def displayHelp(query, params):
        """
        Catches help actions, checks if they are for this module, then calls help(query, params)
        """

    def help(query, params):
        """
        Returns help text describing what the module does.
        Takes params as input so you can override with more complex help lookup.
        """

    def onUnload():
        """
        Called when the module is unloaded. Cleanup, if any.
        """


def ignore(func):
    @wraps(func)
    def wrapped(inst, message):
        if inst.checkIgnoreList(message):
            return
        return func(inst, message)

    return wrapped


class BotModule(object):
    def actions(self):
        return [('help', 1, self.displayHelp)]

    def onLoad(self):
        pass

    def hookBot(self, bot):
        self.bot = bot

    def displayHelp(self, query):
        if query[0].lower() == self.__class__.__name__.lower():
            return self.help(query)

    def help(self, query):
        return "This module has no help text"

    def onUnload(self):
        pass

    def checkIgnoreList(self, message):
        """
        @type message: IRCMessage
        @rtype Boolean
        """
        for ignore in self.bot.config.getWithDefault('ignored', []):
            if fnmatch(message.User.String, ignore):
                return True
        return False

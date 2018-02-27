# -*- coding: utf-8 -*-

from zope.interface import Interface


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

    def help(arg):
        """
        Returns help text describing what the module does.
        Takes an arg as input so you can override with more complex help lookup.
        """

    def onUnload():
        """
        Called when the module is unloaded. Cleanup, if any.
        """


class BotModule(object):
    def actions(self):
        return [('help', 1, self.help)]

    def onLoad(self):
        pass

    def hookBot(self, bot):
        self.bot = bot

    def help(self, arg):
        return "This module has no help text"

    def onUnload(self):
        pass

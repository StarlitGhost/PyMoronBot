# -*- coding: utf-8 -*-
"""
Created on Dec 01, 2013

@author: Tyranic-Moron
"""

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
from Data import ignores


class Unignore(CommandInterface):
    triggers = ['unignore']
    help = 'unignore <user> - remove the specified user from the ignore list'

    bot = None

    def onLoad(self):
        if ignores.ignoreList is None:
            ignores.loadList()

    def onUnload(self):
        if ignores.ignoreList is not None and 'Ignore' not in self.bot.moduleHandler.commands:
            ignores.ignoreList = None

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if not self.checkPermissions(message):
            return IRCResponse(ResponseType.Say, 'Only my admins can edit the ignore list', message.ReplyTo)

        if len(message.ParameterList) > 0:
            for user in message.ParameterList:
                if user.lower() in ignores.ignoreList:
                    ignores.ignoreList.remove(user.lower())

            ignores.saveList()
                
            output = 'No longer ignoring user(s) {0}'.format(', '.join(message.ParameterList))

            return IRCResponse(ResponseType.Say, output, message.ReplyTo)

        else:
            return IRCResponse(ResponseType.Say, self.help, message.ReplyTo)

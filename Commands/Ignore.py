# -*- coding: utf-8 -*-
"""
Created on Dec 01, 2013

@author: Tyranic-Moron
"""

from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
import GlobalVars
from Data import ignores


class Ignore(CommandInterface):
    triggers = ['ignore']
    help = 'ignore <user> - ignore all lines from the specified user'

    bot = None

    def onLoad(self):
        if ignores.ignoreList is None:
            ignores.loadList()

    def onUnload(self):
        if ignores.ignoreList is not None and 'Unignore' not in self.bot.moduleHandler.commands:
            ignores.ignoreList = None

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if message.User.Name not in GlobalVars.admins:
            return IRCResponse(ResponseType.Say, 'Only my admins can edit the ignore list', message.ReplyTo)

        if len(message.ParameterList) > 0:
            for user in message.ParameterList:
                if user.lower() not in ignores.ignoreList:
                    ignores.ignoreList.append(user.lower())

            ignores.saveList()

            output = 'Now ignoring user(s) {0}'.format(', '.join(message.ParameterList))

            return IRCResponse(ResponseType.Say, output, message.ReplyTo)

        else:
            if ignores.ignoreList is not None and len(ignores.ignoreList) > 0:
                return IRCResponse(ResponseType.Say,
                                   'Ignored users: {0}'.format(', '.join(sorted(ignores.ignoreList))),
                                   message.ReplyTo)
            else:
                return IRCResponse(ResponseType.Say, 'Not currently ignoring anyone!', message.ReplyTo)

"""
Created on Dec 01, 2013

@author: Tyranic-Moron
"""

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
import GlobalVars
from Data import ignores
from moronbot import MoronBot


class Unignore(CommandInterface):
    triggers = ['unignore']
    help = 'unignore <user> - remove the specified user from the ignore list'

    bot = None

    def onStart(self, bot=MoronBot):
        self.bot = bot
        if ignores.ignoreList is None:
            ignores.loadList()

    def __del__(self):
        if ignores.ignoreList is not None and 'Ignore' not in self.bot.moduleHandler.commands:
            ignores.ignoreList = None

    def execute(self, message=IRCMessage, bot=MoronBot):
        if message.User.Name not in GlobalVars.admins:
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

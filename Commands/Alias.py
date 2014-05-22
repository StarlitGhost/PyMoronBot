# -*- coding: utf-8 -*-
"""
Created on May 21, 2014

@author: HubbeKing, Tyranic-Moron
"""

from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
import GlobalVars


class Alias(CommandInterface):
    triggers = ['alias']
    help = 'alias <alias> <command> <params> - aliases <alias> to the specified command and parameters\n' \
           'you can specify where parameters given to the alias should be inserted with $1, $2, $n. ' \
           'The whole parameter string is $0. $sender and $channel can also be used.'

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if message.User.Name not in GlobalVars.admins:
            return IRCResponse(ResponseType.Say, "Only my admins may create new aliases!", message.ReplyTo)

        if len(message.ParameterList) <= 1:
            return IRCResponse(ResponseType.Say, "Alias what?", message.ReplyTo)

        triggerFound = False
        for (name, command) in self.bot.moduleHandler.commands.items():
            if message.ParameterList[0] in command.triggers:
                return IRCResponse(ResponseType.Say,
                                   "'{}' is already a command!".format(message.ParameterList[0]),
                                   message.ReplyTo)
            if message.ParameterList[1] in command.triggers:
                triggerFound = True

        if not triggerFound:
            return IRCResponse(ResponseType.Say,
                               "'{}' is not a valid command!".format(message.ParameterList[1]),
                               message.ReplyTo)
        if message.ParameterList[0] in self.bot.moduleHandler.commandAliases:
            return IRCResponse(ResponseType.Say,
                               "'{}' is already an alias!".format(message.ParameterList[0]),
                               message.ReplyTo)

        newAlias = []
        for word in message.ParameterList[1:]:
            newAlias.append(word.lower())
        self.bot.moduleHandler.commandAliases[message.ParameterList[0]] = newAlias

        return IRCResponse(ResponseType.Say,
                           "Created a new alias '{}' for '{}'.".format(message.ParameterList[0],
                                                                       " ".join(message.ParameterList[1:])),
                           message.ReplyTo)

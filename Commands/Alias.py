# -*- coding: utf-8 -*-
"""
Created on May 21, 2014

@author: HubbeKing, Tyranic-Moron
"""
import re

from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
import GlobalVars


class Alias(CommandInterface):
    triggers = ['alias', 'unalias', 'aliases']
    help = 'alias <alias> <command/alias> <params> - aliases <alias> to the specified command/alias and parameters\n' \
           'you can specify where parameters given to the alias should be inserted with $1, $2, $n. ' \
           'The whole parameter string is $0. $sender and $channel can also be used.'
    runInThread = True
           
    def onLoad(self):
        if 'Alias' not in self.bot.dataStore:
            self.bot.dataStore['Alias'] = {}

        self.aliases = self.bot.dataStore['Alias']

    def shouldExecute(self, message):
        return True

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if message.Command.lower() not in self.triggers and message.Command.lower() in self.aliases:
            newMessage = self._aliasedMessage(message)
            newCommand = newMessage.Command.lower()
            if newCommand in self.bot.moduleHandler.mappedTriggers:  # aliased command is a valid trigger
                return self.bot.moduleHandler.mappedTriggers[newCommand].execute(newMessage)
            elif newCommand in self.aliases:  # command is an alias of another alias
                newMessage = self._aliasedMessage(message)
                return self.execute(newMessage)

        if message.Command == 'alias':
            return self._alias(message)
        elif message.Command == 'unalias':
            return self._unalias(message)
        elif message.Command == 'aliases':
            return self._aliases(message)

    def _alias(self, message):
        if message.User.Name not in GlobalVars.admins:
            return IRCResponse(ResponseType.Say, 'Only my admins may create new aliases!', message.ReplyTo)

        if len(message.ParameterList) <= 1:
            return IRCResponse(ResponseType.Say, 'Alias what?', message.ReplyTo)

        if message.ParameterList[0] in self.bot.moduleHandler.mappedTriggers:
            return IRCResponse(ResponseType.Say,
                               "'{}' is already a command!".format(message.ParameterList[0]),
                               message.ReplyTo)
        if message.ParameterList[0] in self.aliases:
            return IRCResponse(ResponseType.Say,
                               "'{}' is already an alias!".format(message.ParameterList[0]),
                               message.ReplyTo)

        if message.ParameterList[1] not in self.bot.moduleHandler.mappedTriggers \
                and message.ParameterList[1] not in self.aliases:
            return IRCResponse(ResponseType.Say,
                               "'{}' is not a valid command or alias!".format(message.ParameterList[1]),
                               message.ReplyTo)

        newAlias = message.ParameterList[1:]
        newAlias[0] = newAlias[0].lower()
        self._newAlias(message.ParameterList[0], newAlias)

        return IRCResponse(ResponseType.Say,
                           "Created a new alias '{}' for '{}'.".format(message.ParameterList[0],
                                                                       ' '.join(message.ParameterList[1:])),
                           message.ReplyTo)

    def _unalias(self, message):
        if message.User.Name not in GlobalVars.admins:
            return IRCResponse(ResponseType.Say, 'Only my admins may delete aliases!', message.ReplyTo)

        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say, 'Unalias what?', message.ReplyTo)

        if message.ParameterList[0] not in self.aliases:
            return IRCResponse(ResponseType.Say,
                               "I don't have an alias called '{}'".format(message.ParameterList[0]),
                               message.ReplyTo)

        self._delAlias(message.ParameterList[0])
        return IRCResponse(ResponseType.Say, "Deleted alias '{}'".format(message.ParameterList[0]), message.ReplyTo)

    def _aliases(self, message):
        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say,
                               "Current aliases: {}".format(', '.join(sorted(self.aliases.keys()))),
                               message.ReplyTo)
        elif message.ParameterList[0] in self.aliases:
            return IRCResponse(ResponseType.Say,
                               "'{}' is aliased to: {}".format(message.ParameterList[0],
                                                            ' '.join(self.aliases[message.ParameterList[0]])),
                               message.ReplyTo)
        else:
            return IRCResponse(ResponseType.Say,
                               "'{}' is not a recognized alias".format(message.ParameterList[0]),
                               message.ReplyTo)

    def _newAlias(self, alias, command):
        self.aliases[alias] = command
        self._syncAliases()

    def _delAlias(self, alias):
        del self.aliases[alias]
        self._syncAliases()

    def _syncAliases(self):
        self.bot.dataStore['Alias'] = self.aliases
        self.bot.dataStore.sync()

    def _aliasedMessage(self, message):
        if message.Command not in self.aliases:
            return

        alias = self.aliases[message.Command]
        newMsg = u'{0}{1}'.format(self.bot.commandChar, ' '.join(alias))

        newMsg = newMsg.replace('$sender', message.User.Name)
        if message.Channel is not None:
            newMsg = newMsg.replace('$channel', message.Channel.Name)
        else:
            newMsg = newMsg.replace('$channel', message.User.Name)

        if re.search(r'\$[0-9]+', newMsg):  # if the alias contains numbered param replacement points, replace them
            newMsg = newMsg.replace('$0',  ' '.join(message.ParameterList))
            for i, param in enumerate(message.ParameterList):
                if newMsg.find("${}+".format(i+1)) != -1:
                    newMsg = newMsg.replace("${}+".format(i+1), " ".join(message.ParameterList[i:]))
                else:
                    newMsg = newMsg.replace("${}".format(i+1), param)
        else:  # if there are no numbered replacement points, append the full parameter list instead
            newMsg += ' {}'.format(' '.join(message.ParameterList))

        return IRCMessage(message.Type, message.User.String, message.Channel, newMsg, self.bot)

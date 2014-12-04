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
    runInThread = True
    
    def help(self, message):
        """
        @type message: IRCMessage
        """
        helpDict = {
            u"alias":   u"alias <alias> <command/alias> <params> - aliases <alias> to the specified command/alias and parameters\n" \
                        u"you can specify where parameters given to the alias should be inserted with $1, $2, $n. " \
                        u"The whole parameter string is $0. $sender and $channel can also be used.",
            u"unalias": u"unalias <alias> - deletes the alias <alias>",
            u"aliases": u"aliases [<alias>] - lists all defined aliases, or the contents of the specified alias"
        }
        return helpDict[message.ParameterList[0]]
    
    def onLoad(self):
        if 'Alias' not in self.bot.dataStore:
            self.bot.dataStore['Alias'] = {}

        self.aliases = self.bot.dataStore['Alias']
        for alias in self.aliases:
            self.bot.moduleHandler.mappedTriggers[alias] = self
            
    def onUnload(self):
        for alias in self.aliases:
            del self.bot.moduleHandler.mappedTriggers[alias]

    def shouldExecute(self, message):
        if message.Command.lower() in self.bot.moduleHandler.mappedTriggers:
            return True
        return False

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if message.Command.lower() not in self.triggers and message.Command.lower() in self.aliases:
            newMessage = self._aliasedMessage(message)
            newCommand = newMessage.Command.lower()
            if newCommand in self.bot.moduleHandler.mappedTriggers:  # aliased command is a valid trigger
                return self.bot.moduleHandler.mappedTriggers[newCommand].execute(newMessage)

        if message.Command.lower() == 'alias':
            return self._alias(message)
        elif message.Command.lower() == 'unalias':
            return self._unalias(message)
        elif message.Command.lower() == 'aliases':
            return self._aliases(message)

    def _alias(self, message):
        if message.User.Name not in GlobalVars.admins:
            return IRCResponse(ResponseType.Say, 'Only my admins may create new aliases!', message.ReplyTo)

        if len(message.ParameterList) <= 1:
            return IRCResponse(ResponseType.Say, 'Alias what?', message.ReplyTo)

        if message.ParameterList[0].lower() in self.bot.moduleHandler.mappedTriggers:
            return IRCResponse(ResponseType.Say,
                               u"'{}' is already a command or alias!".format(message.ParameterList[0].lower()),
                               message.ReplyTo)

        if message.ParameterList[1].lower() not in self.bot.moduleHandler.mappedTriggers:
            return IRCResponse(ResponseType.Say,
                               u"'{}' is not a valid command or alias!".format(message.ParameterList[1].lower()),
                               message.ReplyTo)

        newAlias = message.ParameterList[1:]
        newAlias[0] = newAlias[0].lower()
        self._newAlias(message.ParameterList[0].lower(), newAlias)

        return IRCResponse(ResponseType.Say,
                           u"Created a new alias '{}' for '{}'.".format(message.ParameterList[0].lower(),
                                                                        u' '.join(message.ParameterList[1:])),
                           message.ReplyTo)

    def _unalias(self, message):
        if message.User.Name not in GlobalVars.admins:
            return IRCResponse(ResponseType.Say, 'Only my admins may delete aliases!', message.ReplyTo)

        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say, 'Unalias what?', message.ReplyTo)

        if message.ParameterList[0].lower() not in self.aliases:
            return IRCResponse(ResponseType.Say,
                               u"I don't have an alias called '{}'".format(message.ParameterList[0].lower()),
                               message.ReplyTo)

        self._delAlias(message.ParameterList[0].lower())
        return IRCResponse(ResponseType.Say, u"Deleted alias '{}'".format(message.ParameterList[0].lower()), message.ReplyTo)

    def _aliases(self, message):
        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say,
                               u"Current aliases: {}".format(u', '.join(sorted(self.aliases.keys()))),
                               message.ReplyTo)
        elif message.ParameterList[0].lower() in self.aliases:
            return IRCResponse(ResponseType.Say,
                               u"'{}' is aliased to: {}".format(message.ParameterList[0].lower(),
                                                                u' '.join(self.aliases[message.ParameterList[0].lower()])),
                               message.ReplyTo)
        else:
            return IRCResponse(ResponseType.Say,
                               u"'{}' is not a recognized alias".format(message.ParameterList[0].lower()),
                               message.ReplyTo)

    def _newAlias(self, alias, command):
        self.aliases[alias] = command
        self.bot.moduleHandler.mappedTriggers[alias] = self
        self._syncAliases()

    def _delAlias(self, alias):
        del self.aliases[alias]
        del self.bot.moduleHandler.mappedTriggers[alias]
        self._syncAliases()

    def _syncAliases(self):
        self.bot.dataStore['Alias'] = self.aliases
        self.bot.dataStore.sync()

    def _aliasedMessage(self, message):
        if message.Command.lower() not in self.aliases:
            return

        alias = self.aliases[message.Command.lower()]
        newMsg = u'{0}{1}'.format(self.bot.commandChar, ' '.join(alias))

        newMsg = newMsg.replace('$sender', message.User.Name)
        if message.Channel is not None:
            newMsg = newMsg.replace('$channel', message.Channel.Name)
        else:
            newMsg = newMsg.replace('$channel', message.User.Name)

        if re.search(r'\$[0-9]+', newMsg):  # if the alias contains numbered param replacement points, replace them
            newMsg = newMsg.replace('$0',  u' '.join(message.ParameterList))
            for i, param in enumerate(message.ParameterList):
                if newMsg.find(u"${}+".format(i+1)) != -1:
                    newMsg = newMsg.replace(u"${}+".format(i+1), u" ".join(message.ParameterList[i:]))
                else:
                    newMsg = newMsg.replace(u"${}".format(i+1), param)
        else:  # if there are no numbered replacement points, append the full parameter list instead
            newMsg += u' {}'.format(u' '.join(message.ParameterList))

        return IRCMessage(message.Type, message.User.String, message.Channel, newMsg, self.bot)

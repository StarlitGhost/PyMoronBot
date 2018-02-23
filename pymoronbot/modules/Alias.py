# -*- coding: utf-8 -*-
"""
Created on May 21, 2014

@author: HubbeKing, Tyranic-Moron
"""
import re
from collections import OrderedDict
from six import iteritems

from bs4 import UnicodeDammit

from pymoronbot.moduleinterface import ModuleInterface, admin
from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType
from pymoronbot.utils import web


class Alias(ModuleInterface):
    triggers = ['alias']
    runInThread = True

    def onLoad(self):
        if 'Alias' not in self.bot.dataStore:
            self.bot.dataStore['Alias'] = {
                'Aliases': {},
                'Help': {}
            }

        self.aliases = self.bot.dataStore['Alias']['Aliases']
        for alias in self.aliases:
            self.bot.moduleHandler.mappedTriggers[alias] = self

        self.aliasHelpDict = self.bot.dataStore['Alias']['Help']

        self._helpText = u"{1}alias ({0}) - does alias things. "\
                         u"Use '{1}help alias <subcommand>' for subcommand help. ".format(
            u'/'.join(self.subCommands.keys()), self.bot.commandChar)

    def onUnload(self):
        for alias in self.aliases:
            del self.bot.moduleHandler.mappedTriggers[alias]

    @admin("Only my admins may create new aliases!")
    def _add(self, message):
        """add <alias> <command/alias> [<params>] - aliases <alias> to the specified command/alias and parameters.\
        You can specify where parameters given to the alias should be inserted with $1, $2, $n.\
        The whole parameter string is $0. $sender and $channel can also be used"""
        if len(message.ParameterList) <= 2:
            return IRCResponse(ResponseType.Say, u"Alias what?", message.ReplyTo)

        alias = message.ParameterList[1].lower()
        if alias in self.aliases:
            return IRCResponse(ResponseType.Say,
                               u"'{}' is already an alias!".format(alias),
                               message.ReplyTo)

        if alias in self.bot.moduleHandler.mappedTriggers:
            return IRCResponse(ResponseType.Say,
                               u"'{}' is already a command!".format(alias),
                               message.ReplyTo)

        aliased = message.ParameterList[2].lower()
        if aliased not in self.bot.moduleHandler.mappedTriggers:
            return IRCResponse(ResponseType.Say,
                               u"'{}' is not a valid command or alias!".format(aliased),
                               message.ReplyTo)

        newAlias = message.ParameterList[2:]
        newAlias[0] = newAlias[0].lower()
        self._newAlias(alias, newAlias)

        return IRCResponse(ResponseType.Say,
                           u"Created a new alias '{}' for '{}'.".format(alias,
                                                                        u" ".join(newAlias)),
                           message.ReplyTo)

    @admin("Only my admins may delete aliases!")
    def _del(self, message):
        """del <alias> - deletes the alias named <alias>. You can list multiple aliases to delete (space separated)"""
        if len(message.ParameterList) == 1:
            return IRCResponse(ResponseType.Say, u"Delete which alias?", message.ReplyTo)

        deleted = []
        skipped = []
        for aliasName in [alias.lower() for alias in message.ParameterList[1:]]:
            if aliasName not in self.aliases:
                skipped.append(aliasName)
                continue

            deleted.append(aliasName)
            self._delAlias(aliasName)
        return IRCResponse(ResponseType.Say,
                           u"Deleted alias(es) '{}', {} skipped".format(u", ".join(deleted), len(skipped)),
                           message.ReplyTo)

    def _list(self, message):
        """list - lists all defined aliases"""
        return IRCResponse(ResponseType.Say,
                           u"Current aliases: {}"
                           .format(u", ".join(sorted(self.aliases.keys()))),
                           message.ReplyTo)

    def _show(self, message):
        """show <alias> - shows the contents of the specified alias"""
        if len(message.ParameterList) == 1:
            return IRCResponse(ResponseType.Say,
                               u"Show which alias?",
                               message.ReplyTo)
        alias = message.ParameterList[1].lower()
        if alias in self.aliases:
            return IRCResponse(ResponseType.Say,
                               u"'{}' is aliased to: {}".format(alias,
                                                                u" ".join(self.aliases[alias])),
                               message.ReplyTo)
        else:
            return IRCResponse(ResponseType.Say,
                               u"'{}' is not a recognized alias".format(alias),
                               message.ReplyTo)

    @admin("Only my admins may set alias help text!")
    def _help(self, message):
        """help <alias> <alias help> - defines the help text for the given alias"""
        if len(message.ParameterList) == 1:
            return IRCResponse(ResponseType.Say,
                               u"Set the help text for what alias to what?",
                               message.ReplyTo)

        alias = message.ParameterList[1].lower()
        if alias not in self.aliases:
            return IRCResponse(ResponseType.Say,
                               u"There is no alias called '{}'".format(alias),
                               message.ReplyTo)

        if len(message.ParameterList) == 2:
            return IRCResponse(ResponseType.Say,
                               u"You didn't give me any help text to set for {}!".format(alias),
                               message.ReplyTo)

        aliasHelp = u" ".join(message.ParameterList[2:])
        self.aliasHelpDict[alias] = aliasHelp
        return IRCResponse(ResponseType.Say,
                           u"'{}' help text set to '{}'"
                           .format(alias, aliasHelp),
                           message.ReplyTo)

    def _export(self, message):
        """export [<alias name(s)] - exports all aliases - or the specified aliases - to paste.ee, \
        and returns a link"""
        if len(message.ParameterList) > 1:
            # filter the alias dictionary by the listed aliases
            params = [alias.lower() for alias in message.ParameterList[1:]]
            aliases = {alias: self.aliases[alias]
                       for alias in self.aliases
                       if alias in params}
            aliasHelp = {alias: self.aliasHelpDict[alias]
                         for alias in self.aliasHelpDict
                         if alias in params}

            if len(aliases) == 0:
                return IRCResponse(ResponseType.Say,
                                   u"I don't have any of the aliases listed for export",
                                   message.ReplyTo)
        else:
            aliases = self.aliases
            aliasHelp = self.aliasHelpDict

            if len(aliases) == 0:
                return IRCResponse(ResponseType.Say,
                                   u"There are no aliases for me to export!",
                                   message.ReplyTo)

        addCommands = [u"{}alias add {} {}".format(self.bot.commandChar,
                                                   name, u" ".join(command))
                       for name, command in iteritems(aliases)]
        helpCommands = [u"{}alias help {} {}".format(self.bot.commandChar,
                                                     name, helpText)
                        for name, helpText in iteritems(aliasHelp)]

        export = u"{}\n\n{}".format(u"\n".join(sorted(addCommands)),
                                    u"\n".join(sorted(helpCommands)))

        url = web.pasteEE(export,
                               u"Exported {} aliases for {}".format(self.bot.nickname, self.bot.server),
                          60)
        return IRCResponse(ResponseType.Say,
                           u"Exported {} aliases and {} help texts to {}".format(len(addCommands),
                                                                                 len(helpCommands),
                                                                                 url),
                           message.ReplyTo)

    @admin("Only my admins may import aliases!")
    def _import(self, message):
        """import <url> [<alias(es)>] - imports all aliases from the given address, or only the listed aliases"""
        if len(message.ParameterList) < 2:
            return IRCResponse(ResponseType.Say,
                               u"You didn't give a url to import from!",
                               message.ReplyTo)

        if len(message.ParameterList) > 2:
            onlyListed = True
            importList = [alias.lower() for alias in message.ParameterList[2:]]
        else:
            onlyListed = False

        url = message.ParameterList[1]
        try:
            page = web.fetchURL(url)
        except ValueError:
            return IRCResponse(ResponseType.Say,
                               u"'{}' is not a valid URL".format(url),
                               message.ReplyTo)
        if page is None:
            return IRCResponse(ResponseType.Say,
                               u"Failed to open page at {}".format(url),
                               message.ReplyTo)

        text = page.body
        text = UnicodeDammit(text).unicode_markup
        lines = text.splitlines()
        numAliases = 0
        numHelpTexts = 0
        for lineNumber, line in enumerate(lines):
            # Skip over blank lines
            if line == u"":
                continue
            splitLine = line.split()
            if splitLine[0].lower() != u"{}alias".format(self.bot.commandChar):
                return IRCResponse(ResponseType.Say,
                                   u"Line {} at {} does not begin with {}alias".format(lineNumber,
                                                                                       url,
                                                                                       self.bot.commandChar),
                                   message.ReplyTo)
            subCommand = splitLine[1].lower()
            if subCommand not in [u"add", u"help"]:
                return IRCResponse(ResponseType.Say,
                                   u"Line {} at {} is not an add or help command".format(lineNumber, url),
                                   message.ReplyTo)

            aliasName = splitLine[2].lower()
            aliasCommand = splitLine[3:]
            aliasCommand[0] = aliasCommand[0].lower()

            # Skip over aliases that weren't listed, if any were listed
            if onlyListed and aliasName not in importList:
                continue

            if subCommand == u"add":
                self._newAlias(aliasName, aliasCommand)
                numAliases += 1
            elif subCommand == u"help":
                aliasHelp = u" ".join(splitLine[3:])
                self.aliasHelpDict[aliasName] = aliasHelp
                numHelpTexts += 1

        return IRCResponse(ResponseType.Say,
                           u"Imported {} alias(es) and {} help string(s) from {}".format(numAliases,
                                                                                         numHelpTexts,
                                                                                         url),
                           message.ReplyTo)

    subCommands = OrderedDict([
        (u'add', _add),
        (u'del', _del),
        (u'list', _list),
        (u'show', _show),
        (u'help', _help),
        (u'export', _export),
        (u'import', _import)])

    def help(self, message):
        """
        @type message: IRCMessage
        """
        command = message.ParameterList[0].lower()
        if command in self.triggers:
            if len(message.ParameterList) > 1:
                subCommand = message.ParameterList[1].lower()
                if subCommand in self.subCommands:
                    return u'{1}alias {0}'.format(re.sub(r"\s+", u" ", self.subCommands[subCommand].__doc__),
                                                  self.bot.commandChar)
                else:
                    return self._unrecognizedSubcommand(subCommand)
            else:
                return self._helpText
        elif command in self.aliases:
            if command in self.aliasHelpDict:
                return self.aliasHelpDict[command]
            else:
                return u"'{}' is an alias for: {}".format(command, u" ".join(self.aliases[command]))

    def _unrecognizedSubcommand(self, subCommand):
        return u"unrecognized subcommand '{0}', " \
               u"available subcommands for alias are: {1}".format(subCommand, u', '.join(self.subCommands.keys()))

    def shouldExecute(self, message):
        if message.Command.lower() in self.triggers or message.Command.lower() in self.aliases:
            return True
        return False

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if message.Command.lower() in self.triggers:
            if len(message.ParameterList) > 0:
                subCommand = message.ParameterList[0].lower()
                if subCommand not in self.subCommands:
                    return IRCResponse(ResponseType.Say,
                                       self._unrecognizedSubcommand(subCommand),
                                       message.ReplyTo)
                return self.subCommands[subCommand](self, message)
            else:
                return IRCResponse(ResponseType.Say,
                                   self._helpText,
                                   message.ReplyTo)

        elif message.Command.lower() in self.aliases:
            newMessage = self._aliasedMessage(message)
            newCommand = newMessage.Command.lower()

            # aliased command is a valid trigger
            if newCommand in self.bot.moduleHandler.mappedTriggers:
                return self.bot.moduleHandler.mappedTriggers[newCommand].execute(newMessage)

    def _newAlias(self, alias, command):
        self.aliases[alias] = command
        self.bot.moduleHandler.mappedTriggers[alias] = self
        self._syncAliases()

    def _delAlias(self, alias):
        del self.aliases[alias]
        del self.bot.moduleHandler.mappedTriggers[alias]
        if alias in self.aliasHelpDict:
            del self.aliasHelpDict[alias]
        self._syncAliases()

    def _setAliasHelp(self, alias, aliasHelp):
        self.aliasHelpDict[alias] = aliasHelp
        self._syncAliases()

    def _syncAliases(self):
        self.bot.dataStore['Alias']['Aliases'] = self.aliases
        self.bot.dataStore['Alias']['Help'] = self.aliasHelpDict
        self.bot.dataStore.sync()

    def _aliasedMessage(self, message):
        if message.Command.lower() not in self.aliases:
            return

        alias = self.aliases[message.Command.lower()]
        newMsg = u"{0}{1}".format(self.bot.commandChar, ' '.join(alias))

        newMsg = newMsg.replace("$sender", message.User.Name)
        if message.Channel is not None:
            newMsg = newMsg.replace("$channel", message.Channel.Name)
        else:
            newMsg = newMsg.replace("$channel", message.User.Name)

        paramList = [self._mangleReplacementPoints(param) for param in message.ParameterList]

        # if the alias contains numbered param replacement points, replace them
        if re.search(r'\$[0-9]+', newMsg):
            newMsg = newMsg.replace("$0",  u" ".join(paramList))
            for i, param in enumerate(paramList):
                if newMsg.find(u"${}+".format(i+1)) != -1:
                    newMsg = newMsg.replace(u"${}+".format(i+1),
                                            u" ".join(paramList[i:]))
                else:
                    newMsg = newMsg.replace(u"${}".format(i+1), param)
        # if there are no numbered replacement points, append the full parameter list instead
        else:
            newMsg += u" {}".format(u" ".join(paramList))

        newMsg = self._unmangleReplacementPoints(newMsg)

        return IRCMessage(message.Type, message.User.String, message.Channel, newMsg, self.bot)

    @staticmethod
    def _mangleReplacementPoints(string):
        # Replace alias replacement points with something that should never show up in messages/responses
        string = re.sub(r'\$([\w]+)', r'@D\1@', string)
        return string

    @staticmethod
    def _unmangleReplacementPoints(string):
        # Replace the mangled replacement points with unmangled ones
        string = re.sub(r'@D([\w]+)@', r'$\1', string)
        return string

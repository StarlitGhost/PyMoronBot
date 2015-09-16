# -*- coding: utf-8 -*-
"""
Created on May 21, 2014

@author: HubbeKing, Tyranic-Moron
"""
import re
from collections import OrderedDict

from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
import GlobalVars
from Utils import WebUtils
from moronbot import cmdArgs


class Alias(CommandInterface):
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

    def _add(self, message):
        """add <alias> <command/alias> [<params>] - aliases <alias> to the specified command/alias and parameters.\
        You can specify where parameters given to the alias should be inserted with $1, $2, $n.\
        The whole parameter string is $0. $sender and $channel can also be used"""
        if message.User.Name not in GlobalVars.admins:
            return IRCResponse(ResponseType.Say,
                               u"Only my admins may create new aliases!",
                               message.ReplyTo)

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

    def _del(self, message):
        """del <alias> - deletes the alias named <alias>"""
        if message.User.Name not in GlobalVars.admins:
            return IRCResponse(ResponseType.Say,
                               u"Only my admins may delete aliases!",
                               message.ReplyTo)

        if len(message.ParameterList) == 1:
            return IRCResponse(ResponseType.Say, u"Delete which alias?", message.ReplyTo)

        alias = message.ParameterList[1].lower()
        if alias not in self.aliases:
            return IRCResponse(ResponseType.Say,
                               u"I don't have an alias called '{}'".format(alias),
                               message.ReplyTo)

        self._delAlias(alias)
        return IRCResponse(ResponseType.Say,
                           u"Deleted alias '{}'".format(alias),
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

    def _help(self, message):
        """help <alias> <alias help> - defines the help text for the given alias"""
        if message.User.Name not in GlobalVars.admins:
            return IRCResponse(ResponseType.Say,
                               u"Only my admins may set alias help text!",
                               message.ReplyTo)

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
        """export <all/alias name(s)> - exports all aliases - or the specified aliases - to paste.ee, \
        and returns a link"""
        addCommands = [u"{}alias add {} {}".format(self.bot.commandChar,
                                                   name, u" ".join(command))
                       for name, command in self.aliases.iteritems()]
        helpCommands = [u"{}alias help {} {}".format(self.bot.commandChar,
                                                     name, helpText)
                        for name, helpText in self.aliasHelpDict.iteritems()]

        export = u"{}\n\n{}".format(u"\n".join(sorted(addCommands)),
                                    u"\n".join(sorted(helpCommands)))

        url = WebUtils.pasteEE(export,
                               u"Exported {} aliases for {}".format(self.bot.nickname, cmdArgs.server),
                               0)
        return IRCResponse(ResponseType.Say,
                           u"Aliases exported to {}".format(url),
                           message.ReplyTo)

    def _import(self, message):
        """import <url> - imports aliases from the given address"""
        return

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
                    return u'{1}alias {0}'.format(re.sub(ur"\s+", u" ", self.subCommands[subCommand].__doc__),
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
        if message.Command.lower() in self.bot.moduleHandler.mappedTriggers:
            return True
        return False

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if message.Command in self.triggers:
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

        if message.Command.lower() not in self.triggers and message.Command.lower() in self.aliases:
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

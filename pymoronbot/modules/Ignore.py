# -*- coding: utf-8 -*-
"""
Created on Feb 09, 2018

@author: Tyranic-Moron
"""

import re
from collections import OrderedDict

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType
from pymoronbot.moduleinterface import ModuleInterface


class Ignore(ModuleInterface):
    triggers = ['ignore']

    def _add(self, message):
        """add <nick/full hostmask> - adds the specified user to the ignored list.
        You can list multiple users to add them all at once.
        Nick alone will be converted to a glob hostmask, eg: *!user@host"""
        if not self.checkPermissions(message):
            return IRCResponse(ResponseType.Say,
                               u'Only my admins may add new ignores!',
                               message.ReplyTo)

        if len(message.ParameterList) < 2:
            return IRCResponse(ResponseType.Say,
                               u"You didn't give me a user to ignore!",
                               message.ReplyTo)

        for ignore in message.ParameterList[1:]:
            if message.ReplyTo in self.bot.channels:
                if ignore in self.bot.channels[message.ReplyTo].Users:
                    user = self.bot.channels[message.ReplyTo].Users[ignore]
                    ignore = u'*!{}@{}'.format(user.User, user.Hostmask)

            ignores = self.bot.config.getWithDefault('ignored', [])
            ignores.append(ignore)
            self.bot.config['ignored'] = ignores

        self.bot.config.writeConfig()
        return IRCResponse(ResponseType.Say,
                           u"Now ignoring specified users!",
                           message.ReplyTo)

    def _del(self, message):
        """del <full hostmask> - removes the specified user from the ignored list.
        You can list multiple users to remove them all at once."""
        if not self.checkPermissions(message):
            return IRCResponse(ResponseType.Say,
                               u'Only my admins may remove ignores!',
                               message.ReplyTo)

        if len(message.ParameterList) < 2:
            return IRCResponse(ResponseType.Say,
                               u"You didn't give me a user to unignore!",
                               message.ReplyTo)

        deleted = []
        skipped = []
        ignores = self.bot.config.getWithDefault('ignored', [])
        for unignore in message.ParameterList[1:]:
            if message.ReplyTo in self.bot.channels:
                if unignore in self.bot.channels[message.ReplyTo].Users:
                    user = self.bot.channels[message.ReplyTo].Users[unignore]
                    unignore = u'*!{}@{}'.format(user.User, user.Hostmask)

            if unignore not in ignores:
                skipped.append(unignore)
                continue

            ignores.remove(unignore)
            deleted.append(unignore)

        self.bot.config['ignored'] = ignores
        self.bot.config.writeConfig()

        return IRCResponse(ResponseType.Say,
                           u"Removed '{}' from ignored list, {} skipped"
                           .format(u', '.join(deleted), len(skipped)),
                           message.ReplyTo)

    def _list(self, message):
        """list - lists all ignored users"""
        ignores = self.bot.config.getWithDefault('ignored', [])
        return IRCResponse(ResponseType.Say,
                           u"Ignored Users: {}".format(u', '.join(ignores)),
                           message.ReplyTo)

    subCommands = OrderedDict([
        (u'add', _add),
        (u'del', _del),
        (u'list', _list)])

    def help(self, message):
        """
        @type message: IRCMessage
        @rtype str
        """
        if len(message.ParameterList) > 1:
            subCommand = message.ParameterList[1].lower()
            if subCommand in self.subCommands:
                return u'{1}ignore {0}'.format(re.sub(r"\s+", u" ", self.subCommands[subCommand].__doc__),
                                               self.bot.commandChar)
            else:
                return self._unrecognizedSubcommand(subCommand)
        else:
            return self._helpText()

    def _unrecognizedSubcommand(self, subCommand):
        return u"unrecognized subcommand '{}', " \
               u"available subcommands for ignore are: {}".format(subCommand, u', '.join(self.subCommands.keys()))

    def _helpText(self):
        return u"{1}ignore ({0}) - manages ignored users. Use '{1}help ignore <subcommand> for subcommand help.".format(
            u'/'.join(self.subCommands.keys()), self.bot.commandChar)

    def execute(self, message):
        if len(message.ParameterList) > 0:
            subCommand = message.ParameterList[0].lower()
            if subCommand not in self.subCommands:
                return IRCResponse(ResponseType.Say,
                                   self._unrecognizedSubcommand(subCommand),
                                   message.ReplyTo)
            return self.subCommands[subCommand](self, message)
        else:
            return IRCResponse(ResponseType.Say,
                               self._helpText(),
                               message.ReplyTo)
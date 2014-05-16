# -*- coding: utf-8 -*-
"""
Created on May 03, 2014

@author: Tyranic-Moron
"""

from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
import GlobalVars
from moronbot import MoronBot

from Utils import StringUtils

import re


class Chain(CommandInterface):
    triggers = ['chain']
    help = 'chain <command 1> | <command 2> [| <command n>] - chains multiple commands together, feeding the output of each command into the next\n' \
           'syntax: command1 params | command2 %output% | command3 %var%\n' \
           '%output% is the output text of the previous command in the chain\n' \
           '%var% is any extra var that may have been added to the message by commands earlier in the chain'
    runInThread = True

    def execute(self, message, bot):
        """
        @type message: IRCMessage
        @type bot: MoronBot
        """

        # TODO: maybe do this in the command handler?
        # map triggers to commands so we can call them via dict lookup
        mappedTriggers = {}
        for command in bot.moduleHandler.commands.values():
            for trigger in command.triggers:
                mappedTriggers[trigger] = command

        # split on unescaped |
        chain = re.split(r'(?<!\\)\|', message.Parameters)

        # rebuild the user string... TODO: this should probably be part of the User class
        if message.User.User is not None:
            userString = '{0}!{1}@{2}'.format(message.User.Name, message.User.User, message.User.Hostmask)
        else:
            userString = message.User.Name

        response = None

        for link in chain:
            if response is not None:
                link = link.replace('%output%', response.Response)  # replace %output% with output of previous command
            else:
                # replace %output% with empty string if previous command had no output
                # (or this is the first command in the chain, but for some reason has %output% as a param)
                link = link.replace('%output%', '')

            # build a new message out of this 'link' in the chain
            inputMessage = IRCMessage(message.Type, userString, message.Channel, GlobalVars.CommandChar + link.lstrip())
            inputMessage.chained = True  # might be used at some point to tell commands they're being called from Chain

            if inputMessage.Command.lower() in mappedTriggers:
                response = mappedTriggers[inputMessage.Command.lower()].execute(inputMessage, bot)
            else:
                return IRCResponse(ResponseType.Say,
                                   "'{0}' is not a recognized command trigger".format(inputMessage.Command),
                                   message.ReplyTo)

        if response.Response is not None:
            # limit response length (chains can get pretty large)
            response.Response = list(StringUtils.splitUTF8(response.Response.encode('utf-8'), 700))[0]
            response.Response = unicode(response.Response, 'utf-8')
        return response

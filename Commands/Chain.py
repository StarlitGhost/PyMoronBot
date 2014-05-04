'''
Created on May 03, 2014

@author: Tyranic-Moron
'''

from IRCMessage import IRCMessage, IRCChannel
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
import GlobalVars

import re

class Command(CommandInterface):
    triggers = ['chain']
    help = 'chain <command 1> | <command 2> [| <command n>] - chains multiple commands together, feeding the output of each command into the next'\
           'syntax: command1 params | command2 %output% | command3 %var%'\
           '%output% is the output text of the previous command in the chain'\
           '%var% is any extra var that may have been added to the message by commands earlier in the chain'

    def execute(self, message=IRCMessage):

        # maybe do this in the command handler?
        mappedTriggers = {}
        for command in GlobalVars.commands.values():
            for trigger in command.triggers:
                mappedTriggers[trigger] = command

        chain = re.split(r'(?<!\\)\|', message.Parameters)

        if message.User.User is not None:
            userString = '{0}!{1}@{2}'.format(message.User.Name, message.User.User, message.User.Hostmask)
        else:
            userString = message.User.Name

        response = None

        for link in chain:
            if response is not None:
                link = link.replace('%output%', response.Response)
            input = IRCMessage(message.Type, userString, message.Channel, GlobalVars.CommandChar + link.lstrip())
            input.chained = True
            
            if input.Command.lower() in mappedTriggers:
                response = mappedTriggers[input.Command.lower()].execute(input)
            else:
                return IRCResponse(ResponseType.Say, "'{0}' is not a recognized command trigger".format(input.Command), message.ReplyTo)

        return response
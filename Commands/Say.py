"""
Created on Dec 20, 2011

@author: Tyranic-Moron
"""

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface


class Command(CommandInterface):
    triggers = ['say']
    help = 'say <text> - makes the bot repeat the specified text'

    def execute(self, message=IRCMessage):
        if len(message.ParameterList) > 0:
            return IRCResponse(ResponseType.Say, message.Parameters, message.ReplyTo)
        else:
            return IRCResponse(ResponseType.Say, 'Say what?', message.ReplyTo)


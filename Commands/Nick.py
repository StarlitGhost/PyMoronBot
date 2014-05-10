"""
Created on Dec 20, 2011

@author: Tyranic-Moron
"""

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
import GlobalVars


class Command(CommandInterface):
    triggers = ['nick', 'name']
    help = "nick <nick> - changes the bot's nick to the one specified"

    def execute(self, message=IRCMessage):
        if message.User.Name not in GlobalVars.admins:
            return IRCResponse(ResponseType.Say, 'Only my admins can change my name', message.ReplyTo)

        if len(message.ParameterList) > 0:
            return IRCResponse(ResponseType.Raw, 'NICK %s' % (message.ParameterList[0]), '')
        else:
            return IRCResponse(ResponseType.Say, 'Change my %s to what?' % message.Command, message.ReplyTo)

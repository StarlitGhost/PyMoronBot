"""
Created on Dec 20, 2011

@author: Tyranic-Moron
"""

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
import GlobalVars


class Command(CommandInterface):
    triggers = ['leave', 'gtfo']
    help = "leave/gtfo - makes the bot leave the current channel"

    def execute(self, message=IRCMessage):
        if message.User.Name not in GlobalVars.admins:
            return IRCResponse(ResponseType.Say, 'Only my admins can tell me to %s' % message.Command, message.ReplyTo)
        
        if len(message.ParameterList) > 0:
            return IRCResponse(ResponseType.Raw, 'PART %s :%s' % (message.ReplyTo, message.Parameters), '')
        else:
            return IRCResponse(ResponseType.Raw, 'PART %s :toodles!' % (message.ReplyTo), '')

"""
Created on Dec 20, 2011

@author: Tyranic-Moron
"""

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
import GlobalVars


class Command(CommandInterface):
    triggers = ['source']
    help = "source - returns a link to {0}'s source".format(GlobalVars.CurrentNick)

    def execute(self, message=IRCMessage):
        return IRCResponse(ResponseType.Say, GlobalVars.source, message.ReplyTo)

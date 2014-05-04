'''
Created on Dec 20, 2011

@author: Tyranic-Moron
'''

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
import GlobalVars

import re

class Command(CommandInterface):
    triggers = ['source']
    help = "source - returns a link to %s's source" % GlobalVars.CurrentNick

    def execute(self, message):
        return IRCResponse(ResponseType.Say, GlobalVars.source, message.ReplyTo)


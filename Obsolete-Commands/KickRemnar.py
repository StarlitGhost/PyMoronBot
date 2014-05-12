"""
Created on Dec 18, 2011

@author: Tyranic-Moron
"""

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface

import re


class Command(CommandInterface):
    acceptedTypes = ['PRIVMSG', 'ACTION']
    help = 'Guards against the terrible influx of Mormon Jesus'

    def shouldExecute(self, message=IRCMessage, bot=MoronBot):
        if message.Type not in self.acceptedTypes:
            return False
        match = re.search('([^a-zA-Z]|^)mormon jesus([^a-zA-Z]|$)',
                          message.MessageString,
                          re.IGNORECASE)
        if match and message.User.Name.lower() == 'remnar':
            return True
        return False

    def execute(self, message=IRCMessage, bot=MoronBot):
            return IRCResponse(ResponseType.Raw,
                               'KICK %s remnar ::I' % message.ReplyTo,
                               '')
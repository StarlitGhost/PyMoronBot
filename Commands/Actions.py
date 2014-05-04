from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
from GlobalVars import *

import re

class Command(CommandInterface):
    acceptedTypes = ['ACTION']
    help = 'Responds to various actions'
    
    def shouldExecute(self, message):
        if message.Type in self.acceptedTypes:
            return True

    def execute(self, message):
        match = re.search("^(?P<action>(pokes|gropes|molests|slaps|kicks|rubs|hugs|cuddles|glomps)),?[ ]%s([^a-zA-Z0-9_\|`\[\]\^-]|$)" % CurrentNick,
                          message.MessageString,
                          re.IGNORECASE)
        if match:
            return IRCResponse(ResponseType.Do,
                               '%s %s' % (match.group('action'), message.User.Name),
                               message.ReplyTo)

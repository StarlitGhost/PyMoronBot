from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
from GlobalVars import *

import re

class Instantiate(Function):
    Help = 'Responds to various actions'

    def GetResponse(self, message):
        if message.Type != 'ACTION':
            return
        
        match = re.search("^(?P<action>(pokes|gropes|molests|slaps|kicks|rubs|hugs|cuddles|glomps)),?[ ]%s([^a-zA-Z0-9_\|`\[\]\^-]|$)" % CurrentNick,
                          message.MessageString,
                          re.IGNORECASE)
        if match:
            return IRCResponse(ResponseType.Do,
                               '%s %s' % (match.group('action'), message.User.Name),
                               message.ReplyTo)

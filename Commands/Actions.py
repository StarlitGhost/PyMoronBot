from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
import GlobalVars

import re


class Command(CommandInterface):
    acceptedTypes = ['ACTION']
    help = 'Responds to various actions'

    def shouldExecute(self, message=IRCMessage):
        if message.Type in self.acceptedTypes:
            return True

    def execute(self, message=IRCMessage):
        actions = ['pokes',
                   'gropes',
                   'molests',
                   'slaps',
                   'kicks',
                   'rubs',
                   'hugs',
                   'cuddles',
                   'glomps']
        regex = r"^(?P<action>({0})),?[ ]{1}([^a-zA-Z0-9_\|`\[\]\^-]|$)"
        match = re.search(
            regex.format('|'.join(actions), GlobalVars.CurrentNick),
            message.MessageString,
            re.IGNORECASE)
        if match:
            return IRCResponse(ResponseType.Do,
                               '%s %s' % (match.group('action'), message.User.Name),
                               message.ReplyTo)

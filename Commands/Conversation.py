from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
from GlobalVars import *

import re

class Command(CommandInterface):
    help = 'Responds to greetings and such'

    def shouldExecute(self, message):
        if message.Type in self.acceptedTypes:
            return True

    def execute(self, message):
        match = re.search("^(?P<greeting>(wa+s+|')?so?u+p|hi(ya)?|hey|hello|'?lo|(good |g'?)?((mornin|evenin)[g']?|ni(ght|ni)|afternoon)|greetings|bonjour|salut|howdy|'?yo|o?hai|mojn|hej|dongs|ahoy( hoy)?|salutations|g'?day|hola|bye|herrow)( there)?,?[ ]%s([^a-zA-Z0-9_\|`\[\]\^-]|$)" % CurrentNick,
                          message.MessageString,
                          re.IGNORECASE)
        if match:
            return IRCResponse(ResponseType.Say,
                               '%s %s' % (match.group('greeting'), message.User.Name),
                               message.ReplyTo)

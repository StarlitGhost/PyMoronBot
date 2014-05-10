from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
import GlobalVars

import re


class Command(CommandInterface):
    help = 'Responds to greetings and such'

    def shouldExecute(self, message=IRCMessage):
        if message.Type in self.acceptedTypes:
            return True

    def execute(self, message=IRCMessage):
        greetings = ["(wa+s+|')?so?u+p",
                     "hi(ya)?",
                     "hello",
                     "hey",
                     "'?[yl]o",
                     "(good |g'?)?((mornin|evenin)[g']?|ni(ght|ni)|afternoon|day)",
                     "greetings",
                     "bonjour",
                     "salut(ations)?",
                     "howdy",
                     "o?hai",
                     "mojn",
                     "hej",
                     "dongs",
                     "ahoy( hoy)?",
                     "hola",
                     "bye",
                     "herrow"
                     ]

        regex = r"^(?P<greeting>{0})( there)?,?[ ]{1}([^a-zA-Z0-9_\|`\[\]\^-]|$)".format('|'.join(greetings),
                                                                                         GlobalVars.CurrentNick)

        match = re.search(regex,
                          message.MessageString,
                          re.IGNORECASE)
        if match:
            return IRCResponse(ResponseType.Say,
                               '{0} {1}'.format(match.group('greeting'), message.User.Name),
                               message.ReplyTo)

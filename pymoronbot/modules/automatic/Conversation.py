# -*- coding: utf-8 -*-
from twisted.plugin import IPlugin
from pymoronbot.moduleinterface import IModule, BotModule
from zope.interface import implementer

import re

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType


@implementer(IPlugin, IModule)
class Conversation(BotModule):
    def actions(self):
        return super(Conversation, self).actions() + [('message-channel', 1, self.handleConversation),
                                                      ('message-user', 1, self.handleConversation)]

    def help(self, arg):
        return 'Responds to greetings and such'

    def handleConversation(self, message):
        """
        @type message: IRCMessage
        """
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
                                                                                         self.bot.nickname)

        match = re.search(regex,
                          message.MessageString,
                          re.IGNORECASE)
        if match:
            return IRCResponse(ResponseType.Say,
                               '{0} {1}'.format(match.group('greeting'), message.User.Name),
                               message.ReplyTo)


conversation = Conversation()

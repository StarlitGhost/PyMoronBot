# -*- coding: utf-8 -*-
from twisted.plugin import IPlugin
from pymoronbot.moduleinterface import IModule, BotModule, ignore
from zope.interface import implementer

import re

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType


@implementer(IPlugin, IModule)
class Actions(BotModule):
    def actions(self):
        return super(Actions, self).actions() + [('action-channel', 1, self.handleAction),
                                                 ('action-user', 1, self.handleAction)]

    def help(self, arg):
        return 'Responds to various actions'

    @ignore
    def handleAction(self, message):
        """
        @type message: IRCMessage
        """
        regex = r"^(?P<action>(\w+s)),?[ ]{}([^a-zA-Z0-9_\|`\[\]\^-]|$)"
        match = re.search(
            regex.format(self.bot.nickname),
            message.MessageString,
            re.IGNORECASE)
        if match:
            return IRCResponse(ResponseType.Do,
                               re.sub(self.bot.nickname, message.User.Name, message.MessageString, flags=re.IGNORECASE),
                               message.ReplyTo)


actions = Actions()

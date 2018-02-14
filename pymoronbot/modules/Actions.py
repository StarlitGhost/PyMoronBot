# -*- coding: utf-8 -*-
import re

from pymoronbot.moduleinterface import ModuleInterface
from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType


class Actions(ModuleInterface):
    acceptedTypes = ['ACTION']
    help = 'Responds to various actions'

    def shouldExecute(self, message):
        """
        @type message: IRCMessage
        """
        if message.Type in self.acceptedTypes:
            return True

    def execute(self, message):
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

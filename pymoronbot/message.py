# -*- coding: utf-8 -*-
from enum import Enum
import re

from pymoronbot.user import IRCUser
from pymoronbot.channel import IRCChannel


class TargetTypes(Enum):
    CHANNEL = 1
    USER = 2
            

class IRCMessage(object):
    def __init__(self, msgType, user, channel, message, bot, metadata=None):
        """
        @type msgType: str
        @type user: str
        @type channel: IRCChannel
        @type message: unicode
        @type bot: MoronBot
        @type metadata: dict
        """
        if metadata is None:
            metadata = {}
        self.Metadata = metadata

        if isinstance(message, bytes):
            unicodeMessage = message.decode('utf-8', 'ignore')
        else:  # Already utf-8?
            unicodeMessage = message
        self.Type = msgType
        self.MessageList = unicodeMessage.strip().split(' ')
        self.MessageString = unicodeMessage
        self.User = IRCUser(user)

        self.Channel = None
        if channel is None:
            self.ReplyTo = self.User.Name
            self.TargetType = TargetTypes.USER
        else:
            self.Channel = channel
            # I would like to set this to the channel object but I would probably break functionality if I did :I
            self.ReplyTo = channel.Name
            self.TargetType = TargetTypes.CHANNEL

        self.Command = ''
        self.Parameters = ''
        self.ParameterList = []

        if self.MessageList[0].startswith(bot.commandChar):
            self.Command = self.MessageList[0][len(bot.commandChar):]
            if self.Command == '':
                self.Command = self.MessageList[1]
                self.Parameters = u' '.join(self.MessageList[2:])
            else:
                self.Parameters = u' '.join(self.MessageList[1:])
        elif re.match('{}[:,]?'.format(re.escape(bot.nickname)), self.MessageList[0], re.IGNORECASE):
            if len(self.MessageList) > 1:
                self.Command = self.MessageList[1]
                self.Parameters = u' '.join(self.MessageList[2:])

        if self.Parameters.strip():
            self.ParameterList = self.Parameters.split(' ')

            self.ParameterList = [param for param in self.ParameterList if param != '']

            if len(self.ParameterList) == 1 and not self.ParameterList[0]:
                self.ParameterList = []

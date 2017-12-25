# -*- coding: utf-8 -*-
import ServerInfo
from enum import Enum
import re


class TargetTypes(Enum):
    CHANNEL = 1
    USER = 2


class IRCChannel(object):
    def __init__(self, name):
        """
        @type name: str
        """
        self.Name = name
        self.Topic = ''
        self.TopicSetBy = ''
        self.Users = {}
        self.Ranks = {}
        self.Modes = {}

    def __str__(self):
        return self.Name

    def getHighestStatusOfUser(self, nickname):
        if not self.Ranks[nickname]:
            return None

        for mode in ServerInfo.StatusOrder:
            if mode in self.Ranks[nickname]:
                return mode

        return None


class IRCUser(object):
    def __init__(self, user):
        """
        @type user: str
        """
        self.User = None
        self.Hostmask = None

        if '!' in user:
            userArray = user.split('!')
            self.Name = userArray[0]
            if len(userArray) > 1:
                userArray = userArray[1].split('@')
                self.User = userArray[0]
                self.Hostmask = userArray[1]
            self.String = "{}!{}@{}".format(self.Name, self.User, self.Hostmask)
        else:
            self.Name = user
            self.String = "{}!{}@{}".format(self.Name, None, None)
            

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

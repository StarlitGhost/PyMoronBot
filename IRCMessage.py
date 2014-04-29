from enumType import enum
import GlobalVars, ServerInfo

TargetTypes = enum('CHANNEL', 'USER')

class IRCChannel(object):
    def __init__(self, name):
        self.Name = name
        self.Topic = ''
        self.TopicSetBy = ''
        self.Users = {}
        self.Ranks = {}
        self.Modes = {}

    def getHighestStatusOfUser(self, nickname):
        if not self.Ranks[nickname]:
            return None

        for mode in ServerInfo.StatusOrder:
            if mode in self.Ranks[nickname]:
                return mode

        return None

class IRCUser(object):
    Hostmask = None
    Name = None
    User = None

    def __init__(self, user):
        userArray = user.split('!')
        self.Name = userArray[0]
        if len(userArray) > 1:
            userArray = userArray[1].split('@')
            self.User = userArray[0]
            self.Hostmask = userArray[1]

class IRCMessage(object):
    Type = None
    User = None
    TargetType = TargetTypes.CHANNEL
    ReplyTo = None
    MessageList = []
    MessageString = None
    Channel = None
    
    Command = ''
    Parameters = ''
    ParameterList = []

    def __init__(self, type, user, channel, message):
        unicodeMessage = message.decode('utf-8', 'ignore')
        self.Type = type
        self.MessageList = unicodeMessage.strip().split(' ')
        self.MessageString = unicodeMessage
        self.User = IRCUser(user)
        if channel == None:
            self.ReplyTo = self.User.Name
            self.TargetType = TargetTypes.USER
        else:
            self.Channel = channel
            self.ReplyTo = channel.Name # I would like to set this to the channel object but I would probably break functionality if I did :I
            self.TargetType = TargetTypes.CHANNEL

        if self.MessageList[0].startswith(GlobalVars.CommandChar):
            self.Command = self.MessageList[0][len(GlobalVars.CommandChar):]
            if self.Command == '':
                self.Command = self.MessageList[1]
                self.Parameters = u' '.join(self.MessageList[2:])
            else:
                self.Parameters = u' '.join(self.MessageList[1:])
        elif self.MessageList[0].startswith(GlobalVars.CurrentNick) and len(self.MessageList) > 1:
            self.Command = self.MessageList[1]
            self.Parameters = u' '.join(self.MessageList[2:])

        if self.Parameters.strip():
            self.ParameterList = self.Parameters.split(' ')

            self.ParameterList = [param for param in self.ParameterList if param != '']

            if len(self.ParameterList) == 1 and not self.ParameterList[0]:
                self.ParameterList = []

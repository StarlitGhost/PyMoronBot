from enumType import enum
import GlobalVars

TargetTypes = enum('CHANNEL', 'USER')

class UserStruct:
    Hostmask = ''
    Name = ''
    User = ''

    def __init__(self, user):
        userArray = user.split('!')
        self.Name = userArray[0]
        userArray = userArray[1].split('@')
        self.User = userArray[0]
        self.Hostmask = userArray[1]

class IRCMessage:
    Type = ''
    User = None
    TargetType = TargetTypes.CHANNEL
    ReplyTo = ''
    MessageList = []
    MessageString = u''
    
    Command = u''
    Parameters = u''
    ParameterList = []

    def __init__(self, type, user, channel, message):
        unicodeMessage = message.decode('utf-8')
        self.Type = type
        self.MessageList = unicodeMessage.strip().split(' ')
        self.MessageString = unicodeMessage
        self.User = UserStruct(user)
        if channel == GlobalVars.CurrentNick:
            self.ReplyTo = self.User.Name
        else:
            self.ReplyTo = channel
        if (channel.startswith('#')):
            self.TargetType = TargetTypes.CHANNEL
        else:
            self.TargetType = TargetTypes.USER
        
        if (self.MessageList[0].startswith('\\')):
            self.Command = self.MessageList[0][1:]
            self.Parameters = unicodeMessage[len(self.Command)+2:]
            if self.Parameters.strip() is not '':
                self.ParameterList = self.Parameters.split(' ')
        

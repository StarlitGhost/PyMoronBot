from enumType import enum

ResponseType = enum('Say','Do','Notice','Raw')

class IRCResponse:
    def __init__(self, messageType, response, target):
        self.Type = messageType
        self.Response = unicode(response, 'utf-8')
        self.Target = target


from moronbot import MoronBot
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType


class CommandInterface(object):
    triggers = []
    acceptedTypes = ['PRIVMSG']
    help = '<no help defined (yet)>'
    runInThread = False

    priority = 0
    
    def __init__(self, bot=MoronBot):
        self.onStart(bot)

    def onStart(self, bot=MoronBot):
        pass

    def shouldExecute(self, message=IRCMessage, bot=MoronBot):
        if message.Type not in self.acceptedTypes:
            return False
        if message.Command.lower() not in self.triggers:
            return False
        
        return True

    def execute(self, message=IRCMessage, bot=MoronBot):
        return IRCResponse(ResponseType.Say, '<command not yet implemented>', message.ReplyTo)

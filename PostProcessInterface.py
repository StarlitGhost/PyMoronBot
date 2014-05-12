from moronbot import MoronBot
from IRCResponse import IRCResponse, ResponseType


class PostProcessInterface(object):
    acceptedTypes = [ResponseType.Say, ResponseType.Do, ResponseType.Notice]
    help = '<no help defined (yet)>'
    runInThread = False
    priority = 0

    def __init__(self, bot=MoronBot):
        self.onStart(bot)

    def onStart(self, bot=MoronBot):
        pass

    def shouldExecute(self, response=IRCResponse, bot=MoronBot):
        if response.Type in self.acceptedTypes:
            return True

    def execute(self, response=IRCResponse, bot=MoronBot):
        return response

from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from moronbot import MoronBot


class Apples(CommandInterface):
    help = 'playapples, stopapples - For when you need a 4th for Apples to Apples (will always pick 0)'

    playApples = 0

    def shouldExecute(self, message=IRCMessage, bot=MoronBot):
        if message.Type in self.acceptedTypes:
            return True

    def execute(self, message=IRCMessage, bot=MoronBot):
        if message.Command.lower() == "playapples":
            self.playApples = 1
            return IRCResponse(ResponseType.Say, "!join", message.ReplyTo)
        elif message.Command.lower() == "stopapples":
            self.playApples = 0
            return IRCResponse(ResponseType.Say, "!leave", message.ReplyTo)
        elif self.playApples == 1 and message.User.Name.lower() == "robobo":
            msgArr = message.MessageList
            name = msgArr.pop(0).strip()
            cmd = " ".join(msgArr).strip()
            if cmd == "to Apples! You have 60 seconds to join.":
                return IRCResponse(ResponseType.Say, "!join", message.ReplyTo)
            elif name.lower() == bot.nickname and cmd == "is judging.":
                return IRCResponse(ResponseType.Say, "!pick 0", message.ReplyTo)
            elif name.lower() != bot.nickname and (cmd == "is judging next." or cmd == "is judging first."):
                return IRCResponse(ResponseType.Say, "!play 0", message.ReplyTo)
            elif cmd == "wins the game!" or name == "Sorry,":
                self.playApples = 0

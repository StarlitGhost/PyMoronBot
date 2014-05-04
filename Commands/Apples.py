from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
from GlobalVars import *

import re

class Command(CommandInterface):
    help = 'playapples, stopapples - For when you need a 4th for Apples to Apples (will always pick 0)'

    PlayApples = 0

    def shouldExecute(self, message):
        if message.Type in self.acceptedTypes:
            return True

    def execute(self, message):
        if message.Command.lower() == "playapples":
            self.PlayApples = 1
            return IRCResponse(ResponseType.Say,"!join", message.ReplyTo)
        elif message.Command.lower() == "stopapples":
            self.PlayApples = 0
            return IRCResponse(ResponseType.Say,"!leave", message.ReplyTo)
        elif self.PlayApples == 1 and message.User.Name.lower() == "robobo":
            MsgArr = message.MessageList
            Name = MsgArr.pop(0).strip()
            Cmd = " ".join(MsgArr).strip()
            if Cmd == "to Apples! You have 60 seconds to join.":
                return IRCResponse(ResponseType.Say,"!join", message.ReplyTo)
            elif Name.lower() == "moronbot" and Cmd == "is judging.":
                return IRCResponse(ResponseType.Say,"!pick 0", message.ReplyTo)
            elif Name.lower() != "moronbot" and (Cmd == "is judging next." or Cmd == "is judging first."):
                return IRCResponse(ResponseType.Say,"!play 0", message.ReplyTo)
            elif Cmd == "wins the game!" or Name == "Sorry,":
                self.PlayApples = 0

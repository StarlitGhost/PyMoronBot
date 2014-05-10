from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface


class Command(CommandInterface):
    triggers = ['db7bingo']
    help = "db7bingo - outputs a link for betsy's DB7 Bingo Card"
    
    def execute(self, message=IRCMessage):
        reply = "Betsy's DB7 Bingo Card: https://www.dropbox.com/s/0uihcw5my1zb95e/DesertBusBingo.pdf"
        
        return IRCResponse(ResponseType.Say, reply, message.ReplyTo)

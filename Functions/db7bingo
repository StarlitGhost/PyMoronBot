from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function

import re, math

class Instantiate(Function):
    Help = 'db7bingo - outputs a link for betsy's DB7 Bingo Card'
    
    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('^db7bingo?$', message.Command, re.IGNORECASE)
        if not match:
            return

        reply = "Betsy's DB7 Bingo Card: https://www.dropbox.com/s/0uihcw5my1zb95e/DesertBusBingo.pdf"
        
        return IRCResponse(ResponseType.Say, reply, message.ReplyTo)

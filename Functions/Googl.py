from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
import WebUtils

import re

class Instantiate(Function):
    Help = "googl/shorten <url> - Gives you a shortened version of a url, via Goo.gl"
    
    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('(goo\.?gl|shorten)', message.Command, re.IGNORECASE)
        if not match:
            return
        
        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say, "You didn't give a URL to shorten!", message.ReplyTo)
        
        url = WebUtils.ShortenGoogl(message.Parameters)
        
        return IRCResponse(ResponseType.Say, url, message.ReplyTo)


from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function

import re, math

class Instantiate(Function):
    Help = 'dbhours <money> - tells you how many hours the crew would buss if they had the given amount of money (no dollar signs or commas, eg: 100000 not $100,000)'
    
    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('^dbhours?$', message.Command, re.IGNORECASE)
        if not match:
            return
            
        hours = float(message.ParameterList[0])
        
        money = (1-(1.07**hours))/(-0.07)
        
        reply = "For {0:,} hour(s), the team needs a total of ${1:,.2f}".format(hours, money)
        
        return IRCResponse(ResponseType.Say, reply, message.ReplyTo)

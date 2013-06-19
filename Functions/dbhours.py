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

        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say, self.Help, message.ReplyTo)
        
        hours = 0.0
        money = 0.0
        
        try:
            hours = float(message.ParameterList[0])
        except ValueError:
            return IRCResponse(ResponseType.Say, "Sorry, I don't recognize '{0}' as a number".format(message.ParameterList[0]), message.ReplyTo)
        
        try:
            money = (1-(1.07**hours))/(-0.07)
        except OverflowError:
            return IRCResponse(ResponseType.Say, "The amount of money you would need for that many hours is higher than I can calculate!", message.ReplyTo)
        
        reply = "For {0:,} hour(s), the team needs a total of ${1:,.2f}".format(hours, money)
        
        return IRCResponse(ResponseType.Say, reply, message.ReplyTo)

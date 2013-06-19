from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function

import re, math

class Instantiate(Function):
    Help = 'dbmoney <hours> - tells you how much money the crew would need to bus for the given number of hours'
    
    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('^dbmoney?$', message.Command, re.IGNORECASE)
        if not match:
            return
        
        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say, self.Help, message.ReplyTo)
        
        hours = 0.0
        money = 0.0
        
        try:
            money = float(message.ParameterList[0])
        except ValueError:
            return IRCResponse(ResponseType.Say, "Sorry, I don't recognize '{0}' as a number".format(message.ParameterList[0]), message.ReplyTo)
        
        try:
            hours = math.log((7*money)/100 + 1)/math.log(1.07)
        except OverflowError:
            return IRCResponse(ResponseType.Say, "???", message.ReplyTo)
        
        reply = "With ${0:,.2f}, the team will bus for {1:,.2f} hour(s)".format(money, hours)
        
        return IRCResponse(ResponseType.Say, reply, message.ReplyTo)

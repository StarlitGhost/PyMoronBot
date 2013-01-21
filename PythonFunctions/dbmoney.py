from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function

import re, math

class Instantiate(Function):
    Help = '|dbmoney <hours>'
    
    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('^dbmoney?$', message.Command, re.IGNORECASE)
        if not match:
            return
            
        money = float(message.ParameterList[0])
        
        hours = math.log((7*money)/100 + 1)/math.log(1.07)
        
        reply = "With ${0:,.2f}, the team will bus for {1:,.2f} hour(s)".format(money, hours)
        
        return IRCResponse(ResponseType.Say, reply, message.ReplyTo)

'''
Created on Feb 15, 2013

@author: Emily, Tyranic-Moron
'''

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
from GlobalVars import *

import re

class Instantiate(Function):
    Help = 'Responds with a link to the Betting Pool Form'

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('^bettingpool$', message.Command, re.IGNORECASE)
        if not match:
            return
        
        return IRCResponse(ResponseType.Say,
                           #'Evelyn's Proposal to Emily Betting Pool: https://docs.google.com/forms/d/1loM20-SazvWygILBIB-5Qups0X0TVkXAr5p1f7yzxZg/viewform',
                           'Wager: Loser (guessed the farthest away from the actual date) must give the Winner (guessed the closest) a lap dance upon meeting the next time.'
                           message.ReplyTo)

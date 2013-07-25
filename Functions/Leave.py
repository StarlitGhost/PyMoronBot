'''
Created on Dec 20, 2011

@author: Tyranic-Moron
'''

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
import GlobalVars

import re

class Instantiate(Function):
    Help = "leave/gtfo - makes the bot leave the current channel"

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('^leave|gtfo$', message.Command, re.IGNORECASE)
        if not match:
            return
            
        if message.User.Name not in GlobalVars.admins:
            return IRCResponse(ResponseType.Say, 'Only my admins can tell me to %s' % message.Command, message.ReplyTo)
        
        if len(message.ParameterList) > 0:
            return IRCResponse(ResponseType.Raw, 'PART %s :%s' % (message.ReplyTo, message.Parameters), '')
        else:
            return IRCResponse(ResponseType.Raw, 'PART %s :toodles!' % (message.ReplyTo), '')


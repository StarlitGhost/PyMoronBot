'''
Created on Dec 18, 2011

@author: Tyranic-Moron
'''

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
from GlobalVars import *

import re
import datetime

import psutil

class Instantiate(Function):
    Help = "Tells you the bot's uptime"

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('^uptime$', message.Command, re.IGNORECASE)
        if not match:
            return
        
        uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.BOOT_TIME)
        
        return IRCResponse(ResponseType.Say,
                           'Uptime: %s' % str(uptime).split('.')[0],
                           message.ReplyTo)

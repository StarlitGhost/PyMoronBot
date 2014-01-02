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
    Help = 'Responds with a link to the DB torrents'

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('^torrent$', message.Command, re.IGNORECASE)
        if not match:
            return
        
        return IRCResponse(ResponseType.Say,
                           #'DB6: http://fugiman.com/DesertBus6.torrent | DB5: http://fugiman.com/De5ertBus.torrent',
                           'Torrent Files: http://www.laserdino.com/db7.torrent http://static.fugiman.com/ | Magnet Links: http://mgnet.me/.DB7 http://mgnet.me/.DB6 http://mgnet.me/.DB5',
                           message.ReplyTo)

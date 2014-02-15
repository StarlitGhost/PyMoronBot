'''
Created on Feb 14, 2014

@author: Tyranic-Moron
'''

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
from GlobalVars import *

import re

# matches a sed-style regex pattern (taken from https://github.com/mossblaser/BeardBot/blob/master/modules/sed.py)
# I stripped the unnecessary escapes by using a raw string instead
sedRegex = r"s/(?P<search>(\\\\|(\\[^\\])|[^\\/])+)/(?P<replace>(\\\\|(\\[^\\])|[^\\/])*)((/(?P<flags>.*))?)"

class Instantiate(Function):
    Help = 'matches sed-like regex replacement patterns and attempts to execute them on the latest matching line from the last 10\n'\
            'eg: s/some/all/'

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        pass #TODO: everything!

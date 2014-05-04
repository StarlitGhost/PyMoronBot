'''
Created on Dec 20, 2011

@author: Tyranic-Moron
'''

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
from GlobalVars import *

import re

class Command(CommandInterface):
    triggers = ['stats']
    help = 'stats - Responds with a link to the chat stats webpage(s)'

    def execute(self, message):
        return IRCResponse(ResponseType.Say,
                           #'sss: http://www.moronic-works.co.uk/ | pisg: http://silver.amazon.fooproject.net/pisg/desertbus.html | pisg2: http://pisg.michael-wheeler.org/desertbus.html'
                           'sss: http://www.moronic-works.co.uk/ | pisg: http://pisg.michael-wheeler.org/desertbus.html',
                           message.ReplyTo)

'''
Created on Feb 15, 2013

@author: Emily, Tyranic-Moron
'''

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
from GlobalVars import *

import re, random

class Instantiate(Function):
    Help = 'Responds to boops with pictorial boops!'
    
    boops = ["http://goo.gl/HJzfS", # feline anatomy
             "http://bit.ly/yoMzZ1",
             "http://bit.ly/zA2bUY",
             "http://bit.ly/wQoI8p",
             "http://bit.ly/ACbm0J",
             "http://bit.ly/qNyEZk",
             "http://bit.ly/zJrjGF",
             "http://goo.gl/d054n", # This is called "aversion therapy."
             "http://goo.gl/6IoB0", # my grumpy button, ur pushin' it
             "http://bit.ly/z79CJv",
             "http://bit.ly/yODbYA",
             "http://bit.ly/AdX2cw",
             "http://bit.ly/x9WGoy",
             "http://i.imgur.com/vC5gy.jpg",
             "http://i.imgur.com/xmzLY.gif",
             "http://i.imgur.com/NSAKo.jpg",
             "http://bit.ly/NI0jYk",
             "http://bit.ly/MKZqCJ",
             "http://bit.ly/QA92eW",
             "http://i.imgur.com/wtK1T.jpg",
             "http://goo.gl/Nh4PK",
             "http://goo.gl/ZKmt5",
             "http://goo.gl/Juhcv",
             "http://i.imgur.com/BLQoL61.gif", # darting boop
             ]

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
            
        match = re.search("b(o|0)(o|0)+p", message.MessageString, re.IGNORECASE)
        if match:
            return IRCResponse(ResponseType.Say,
                               'Boop! %s' % self.boops[random.randrange(len(self.boops))],
                               message.ReplyTo)

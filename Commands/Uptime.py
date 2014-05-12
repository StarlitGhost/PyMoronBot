"""
Created on Dec 18, 2011

@author: Tyranic-Moron
"""

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
from moronbot import MoronBot

import datetime

import psutil


class Uptime(CommandInterface):
    triggers = ['uptime']
    help = "uptime - tells you the bot's uptime " \
           "(actually that's a lie right now, it gives you the bot's server's uptime)"

    def execute(self, message=IRCMessage, bot=MoronBot):
        uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.BOOT_TIME)
        
        return IRCResponse(ResponseType.Say,
                           'Uptime: %s' % str(uptime).split('.')[0],
                           message.ReplyTo)

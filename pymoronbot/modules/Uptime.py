# -*- coding: utf-8 -*-
"""
Created on Dec 18, 2011

@author: Tyranic-Moron
"""

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType
from pymoronbot.moduleinterface import ModuleInterface

import datetime

import psutil


class Uptime(ModuleInterface):
    triggers = ['uptime']
    help = "uptime - tells you the bot's uptime " \
           "(actually that's a lie right now, it gives you the bot's server's uptime)"

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.BOOT_TIME)
        
        return IRCResponse(ResponseType.Say,
                           'Uptime: %s' % str(uptime).split('.')[0],
                           message.ReplyTo)

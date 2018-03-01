# -*- coding: utf-8 -*-
"""
Created on Dec 20, 2011

@author: Tyranic-Moron
"""

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType
from pymoronbot.modules.commandinterface import BotCommand


class Leave(BotCommand):
    triggers = ['leave', 'gtfo']
    help = "leave/gtfo - makes the bot leave the current channel"

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if not self.checkPermissions(message):
                return IRCResponse(ResponseType.Say,
                                   '{}Only my admins can tell me to {}'.format('Wow, rude? ' if message.Command == 'gtfo' else '',
                                                                               message.Command),
                                   message.ReplyTo)
        
        if len(message.ParameterList) > 0:
            return IRCResponse(ResponseType.Raw, 'PART {} :{}'.format(message.ReplyTo, message.Parameters), '')
        else:
            return IRCResponse(ResponseType.Raw, 'PART {} :toodles!'.format(message.ReplyTo), '')

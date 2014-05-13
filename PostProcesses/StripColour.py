# -*- coding: utf-8 -*-
"""
Created on May 11, 2014

@author: Tyranic-Moron
"""

from moronbot import MoronBot
from PostProcessInterface import PostProcessInterface
from IRCResponse import IRCResponse
from Utils import StringUtils


class StripColour(PostProcessInterface):

    def shouldExecute(self, response, bot):
        """
        @type response: IRCResponse
        @type bot: MoronBot
        """
        if super(StripColour, self).shouldExecute(response, bot):
            channel = bot.getChannel(response.Target)
            if channel is not None and 'c' in channel.Modes:
                # strip formatting if colours are blocked on the channel
                return True

    def execute(self, response, bot):
        """
        @type response: IRCResponse
        @type bot: MoronBot
        """
        response.Response = StringUtils.stripColours(response.Response)
        return response
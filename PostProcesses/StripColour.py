# -*- coding: utf-8 -*-
"""
Created on May 11, 2014

@author: Tyranic-Moron
"""

from PostProcessInterface import PostProcessInterface
from IRCResponse import IRCResponse
from Utils import StringUtils


class StripColour(PostProcessInterface):

    def shouldExecute(self, response):
        """
        @type response: IRCResponse
        """
        if super(StripColour, self).shouldExecute(response):
            channel = self.bot.getChannel(response.Target)
            if channel is not None and 'c' in channel.Modes:
                # strip formatting if colours are blocked on the channel
                return True

    def execute(self, response):
        """
        @type response: IRCResponse
        """
        response.Response = StringUtils.stripColours(response.Response)
        return response
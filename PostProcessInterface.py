# -*- coding: utf-8 -*-
from moronbot import MoronBot
from IRCResponse import IRCResponse, ResponseType


class PostProcessInterface(object):
    acceptedTypes = [ResponseType.Say, ResponseType.Do, ResponseType.Notice]
    help = '<no help defined (yet)>'
    runInThread = False
    priority = 0

    def __init__(self, bot):
        self.onLoad(bot)

    def onLoad(self, bot):
        """
        @type bot: MoronBot
        """
        pass

    def onUnload(self, bot):
        """
        @type bot: MoronBot
        """
        pass

    def shouldExecute(self, response, bot):
        """
        @type response: IRCResponse
        @type bot: MoronBot
        """
        if response.Type in self.acceptedTypes:
            return True

    def execute(self, response, bot):
        """
        @type response: IRCResponse
        @type bot: MoronBot
        """
        return response
